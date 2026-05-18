#!/usr/bin/env python3
"""
Foundry Local on Azure Local — Model Catalog Sample

Demonstrates the full model catalog lifecycle on a Kubernetes cluster
running Foundry Local on Azure Local:

  1. Query the model catalog
  2. Deploy a model from the catalog
  3. Wait for the deployment to become ready
  4. Run inference against the deployed model
  5. Clean up the deployment

Prerequisites:
  - A Kubernetes cluster with the Foundry Local Inference Operator installed
  - kubectl configured with access to the cluster (kubeconfig)
  - Python 3.9+

Usage:
  # Deploy and run inference with Phi-4 on CPU (default)
  python catalog_sample.py

  # Deploy a specific model on GPU
  python catalog_sample.py --model Phi-4-generic-gpu --compute gpu

  # Query the catalog only (no deployment)
  python catalog_sample.py --catalog-only

  # Skip cleanup (leave deployment running)
  python catalog_sample.py --skip-cleanup

Documentation:
  Foundry Local on Azure Local — Inference Operator docs

See Also:
  - Inference Operator overview and CRD reference
  - Model Catalog > ConfigMap Format and Structure
  - Authentication > API Key Generation and Storage
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import signal
import sys
import time
import urllib3

import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from tabulate import tabulate

# ---------------------------------------------------------------------------
# Constants — grounded to the official Foundry Local on Azure Local docs
# ---------------------------------------------------------------------------

FOUNDRY_API_GROUP = "foundrylocal.azure.com"
FOUNDRY_API_VERSION = "v1"
FOUNDRY_PLURAL = "modeldeployments"
FOUNDRY_NAMESPACE = "foundry-local-operator"
CATALOG_CONFIGMAP = "foundry-local-catalog"

# ModelDeployment states (docs: "Resource Lifecycle" table)
STATE_RUNNING = "Running"
STATE_ERROR = "Error"
STATE_PENDING = "Pending"
STATE_CREATING = "Creating"

# Inference runtimes
#   - User-facing CLI tokens: 'onnx', 'vllm' (short, friendly — match the
#     announcement and blog).
#   - Wire values accepted by the operator CRD: 'onnx-genai', 'vllm', 'maas'.
#     The CRD default is 'onnx-genai', so omitting spec.runtime preserves
#     today's behavior byte-equivalently.
#   - Catalog ConfigMap variants use a 'framework' field; older catalogs may
#     have used 'runtime' on nested variants. Both are tolerated.
RUNTIME_ONNX = "onnx"
RUNTIME_VLLM = "vllm"
RUNTIME_CHOICES = (RUNTIME_ONNX, RUNTIME_VLLM)
DEFAULT_RUNTIME = RUNTIME_ONNX

# Maps the user-facing runtime token to the operator's wire value.
# 'onnx' is intentionally mapped to None so the manifest omits spec.runtime
# and inherits the CRD default ('onnx-genai') — keeps existing default
# deployments byte-equivalent and tolerant of older operator builds.
RUNTIME_WIRE_VALUE = {
    RUNTIME_ONNX: None,
    RUNTIME_VLLM: "vllm",
}

# Catalog 'framework' (or legacy 'runtime') values that map to each runtime.
# Treat missing/unknown framework as ONNX (the historical default).
RUNTIME_FRAMEWORK_ALIASES = {
    RUNTIME_ONNX: {"onnx-genai", "onnx"},
    RUNTIME_VLLM: {"vllm"},
}

# Resource presets per sample model (docs: Quick Start YAML examples).
# Preset keys must match the catalog model alias the user passes via --model.
MODEL_PRESETS = {
    "Phi-4-generic-cpu": {
        "compute": "cpu",
        "runtime": RUNTIME_ONNX,
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "2", "memory": "8Gi"},
            "limits": {"cpu": "4", "memory": "24Gi"},
        },
    },
    "Phi-4-generic-gpu": {
        "compute": "gpu",
        "runtime": RUNTIME_ONNX,
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "4", "memory": "32Gi"},
            "limits": {"cpu": "8", "memory": "64Gi", "gpu": 1},
        },
        "nodeSelector": {"foundry/workload": "gpu"},
    },
    # vLLM variants — GPU-only. The operator's vLLM planner handles
    # max_model_len, KV-cache size, and batch sizing automatically, so we
    # intentionally do not pin those here.
    # Note: the catalog alias is 'Phi-4-mini-instruct' (verified against
    # the live bug-bash cluster), not the shorter 'Phi-4-mini' that some
    # announcement drafts use.
    "Phi-4-mini-instruct": {
        "compute": "gpu",
        "runtime": RUNTIME_VLLM,
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "4", "memory": "16Gi"},
            "limits": {"cpu": "8", "memory": "32Gi", "gpu": 1},
        },
        "nodeSelector": {"foundry/workload": "gpu"},
    },
    "Phi-4": {
        "compute": "gpu",
        "runtime": RUNTIME_VLLM,
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "8", "memory": "32Gi"},
            "limits": {"cpu": "16", "memory": "64Gi", "gpu": 1},
        },
        "nodeSelector": {"foundry/workload": "gpu"},
    },
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SampleError(Exception):
    """Raised for expected error conditions with user-friendly messages."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def dns_safe(name: str) -> str:
    """Convert a catalog model name to a DNS-1123 compatible deployment name."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9\-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:63]


def print_step(step: int, total: int, msg: str):
    print(f"\n{'='*60}")
    print(f"  Step {step}/{total} — {msg}")
    print(f"{'='*60}\n")


def print_context_info(namespace: str):
    """Print the current Kubernetes context so users know which cluster
    will be modified. Docs: always verify your kubeconfig before mutating."""
    try:
        _, active_context = config.list_kube_config_contexts()
        ctx = active_context.get("name", "unknown")
        cluster = active_context.get("context", {}).get("cluster", "unknown")
        print(f"  Kubernetes context : {ctx}")
        print(f"  Cluster            : {cluster}")
        print(f"  Target namespace   : {namespace}")
    except Exception:
        print("  Kubernetes context : (could not determine — using in-cluster config?)")


def check_crd_exists(k8s_ext: client.ApiextensionsV1Api):
    """Verify the ModelDeployment CRD is installed before attempting to
    create resources. Docs: Step 3 – Verify the Operator is Running."""
    crd_name = f"{FOUNDRY_PLURAL}.{FOUNDRY_API_GROUP}"
    try:
        k8s_ext.read_custom_resource_definition(crd_name)
        print(f"  ✓ CRD '{crd_name}' found")
    except ApiException as e:
        if e.status == 404:
            raise SampleError(
                f"CRD '{crd_name}' not found.\n"
                "    Is the Inference Operator installed?\n"
                "    See docs: Quick Start > Step 2 – Install Inference Operator"
            )
        raise


# ---------------------------------------------------------------------------
# Step 1 — Query the Model Catalog
# Docs: "Model Catalog > ConfigMap Format and Structure"
# ---------------------------------------------------------------------------


def query_catalog(k8s_core: client.CoreV1Api, namespace: str) -> list[dict]:
    """Read the foundry-local-catalog ConfigMap and parse the model list.

    The catalog is a ConfigMap with a single key 'catalog.json' containing
    model metadata synced from the Azure AI Foundry catalog API.
    """
    try:
        cm = k8s_core.read_namespaced_config_map(CATALOG_CONFIGMAP, namespace)
    except ApiException as e:
        if e.status == 404:
            raise SampleError(
                f"ConfigMap '{CATALOG_CONFIGMAP}' not found in '{namespace}'.\n"
                "    The catalog may not have synced yet.\n"
                "    Try: kubectl create job --from=cronjob/foundry-local-catalog-sync "
                f"manual-sync -n {namespace}"
            )
        raise

    raw = cm.data.get("catalog.json") if cm.data else None
    if not raw:
        raise SampleError("ConfigMap exists but 'catalog.json' key is empty.")

    try:
        catalog = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SampleError(f"Failed to parse catalog.json: {exc}")

    models = catalog.get("models", [])

    last_sync = ""
    if cm.metadata.annotations:
        last_sync = cm.metadata.annotations.get("foundry.azure.com/last-sync", "")

    print(f"  Catalog version : {catalog.get('version', 'N/A')}")
    print(f"  Last sync       : {last_sync or 'N/A'}")
    print(f"  Total models    : {catalog.get('total', len(models))}")

    return models


def entry_runtime(entry: dict) -> str:
    """Return the user-facing runtime token ('onnx' or 'vllm') for a catalog
    entry — works for both schemas the operator has shipped:

      - Flat schema (current):  model entry has a top-level 'framework' field
      - Nested schema (legacy): variant has a 'runtime' field

    Unknown / missing values fall back to 'onnx', which is the historical
    default for Foundry Local.

    Docs: "Model Catalog > ConfigMap Format and Structure"
    """
    framework = (entry.get("framework") or entry.get("runtime") or "").lower()
    for user_token, wire_set in RUNTIME_FRAMEWORK_ALIASES.items():
        if framework in wire_set:
            return user_token
    return DEFAULT_RUNTIME


def _inference_model_id(model_id: str, alias: str, runtime: str) -> str:
    """Return the model identifier the inference server expects.

    Inference model-id conventions differ by runtime (verified on a live
    Foundry Local on Azure Local operator, version 0.260517.6):

      * ONNX-GenAI servers respond to '<name>:<version>'        (e.g. qwen2.5-0.5b-instruct-generic-cpu:4)
      * vLLM servers respond to '<alias>'                       (e.g. Phi-4-mini-instruct)

    Using the wrong format yields a 404 NotFoundError from the server.
    """
    if runtime == RUNTIME_VLLM and alias:
        return alias
    return model_id


def _build_variant_result(model: dict, variant: dict | None,
                          compute_hint: str = "") -> dict:
    """Project a (model, variant) pair into the shape callers expect.

    Pass variant=None for catalogs using the flat schema where the model
    entry itself is the deployable unit. In that case compute is taken
    from compute_hint (the value the user requested) because the flat
    schema doesn't expose compute on the catalog entry.
    """
    if variant is not None:
        runtime = entry_runtime(variant) if variant.get("runtime") else entry_runtime(model)
        result = {
            "alias": model.get("alias", ""),
            "model_id": variant["id"],
            "compute": variant.get("compute", "") or compute_hint,
            "runtime": runtime,
            "displayName": model.get("displayName", ""),
            "task": model.get("task", ""),
            "fileSizeBytes": variant.get("fileSizeBytes", 0),
        }
    else:
        runtime = entry_runtime(model)
        result = {
            "alias": model.get("alias", ""),
            "model_id": model.get("id", ""),
            "compute": compute_hint,
            "runtime": runtime,
            "displayName": model.get("displayName", ""),
            "task": model.get("task", ""),
            "fileSizeBytes": model.get("fileSizeBytes", 0),
        }
    result["inference_model_id"] = _inference_model_id(
        result["model_id"], result["alias"], result["runtime"])
    return result


def display_catalog(models: list[dict]):
    """Display the catalog in a table.

    Supports both the flat schema (current operator: each model is a single
    deployable entry with a top-level 'framework' field) and the legacy
    nested schema (model has a non-empty 'variants' list with per-variant
    'compute' / 'runtime' / 'fileSizeBytes' fields). The RUNTIME column
    surfaces ONNX vs vLLM so the two are easy to tell apart.
    """
    rows = []
    for m in models:
        variants = m.get("variants") or []
        if variants:
            # Legacy nested schema
            for v in variants:
                size_gb = round(v.get("fileSizeBytes", 0) / (1024**3), 2)
                rows.append([
                    m.get("alias", ""),
                    (v.get("compute") or "").upper() or "—",
                    entry_runtime(v) if v.get("runtime") else entry_runtime(m),
                    f"{size_gb}GB" if size_gb else "—",
                    v.get("id", ""),
                ])
        else:
            # Flat schema — model entry is the variant
            size_bytes = m.get("fileSizeBytes", 0)
            size_str = f"{round(size_bytes / (1024**3), 2)}GB" if size_bytes else "—"
            rows.append([
                m.get("alias", ""),
                (m.get("compute") or "").upper() or "—",
                entry_runtime(m),
                size_str,
                m.get("id", ""),
            ])

    print(tabulate(rows,
                   headers=["ALIAS", "DEVICE", "RUNTIME", "SIZE", "MODEL_ID"],
                   tablefmt="simple"))


def resolve_variant(models: list[dict], model_name: str, version: str | None,
                    compute: str, runtime: str | None = None) -> dict | None:
    """Find a catalog entry matching the requested model name, version,
    compute, and runtime.

    Handles both the flat schema (current operator) and the legacy nested
    schema with per-variant detail. When the catalog doesn't expose
    'compute' on its entries (flat schema), compute is not used as a
    filter — the operator handles scheduling based on the manifest's
    spec.compute.

    When version is None, auto-detects the latest version from the catalog.
    """
    runtime_filter = runtime.lower() if runtime else None
    requested_compute = (compute or "").lower()

    def _runtime_matches(entry: dict) -> bool:
        return runtime_filter is None or entry_runtime(entry) == runtime_filter

    for m in models:
        variants = m.get("variants") or []
        if variants:
            # Legacy nested schema
            if version is not None:
                target_id = f"{model_name}:{version}"
                for v in variants:
                    if (v.get("id") == target_id
                            and (v.get("compute") or "").lower() == requested_compute
                            and _runtime_matches(v if v.get("runtime") else m)):
                        return _build_variant_result(m, v, compute)
            else:
                if m.get("displayName") == model_name or m.get("alias") == model_name:
                    for v in variants:
                        if ((v.get("compute") or "").lower() == requested_compute
                                and _runtime_matches(v if v.get("runtime") else m)):
                            return _build_variant_result(m, v, compute)
        else:
            # Flat schema — match the model entry itself
            if m.get("alias") != model_name and m.get("displayName") != model_name:
                continue
            if not _runtime_matches(m):
                continue
            if version is not None:
                m_version = str(m.get("modelVersion") or "")
                m_id = m.get("id", "")
                if m_version != version and m_id != f"{model_name}:{version}":
                    continue
            # No compute filter — flat schema doesn't expose it on the
            # catalog entry; the operator validates against the manifest.
            return _build_variant_result(m, None, compute)

    return None


# ---------------------------------------------------------------------------
# Step 2 — Deploy a Model from the Catalog
# Docs: "Deploying Models > Deploy from Catalog (Inline)"
# ---------------------------------------------------------------------------


def build_deployment_manifest(
    deployment_name: str,
    model_name: str,
    model_version: str,
    compute: str,
    namespace: str,
    runtime: str = DEFAULT_RUNTIME,
) -> dict:
    """Build a ModelDeployment manifest grounded to the official YAML schema.

    Docs reference: "ModelDeployment Reference > Spec Fields" table.

    The optional 'runtime' field selects the inference runtime (ONNX-GenAI
    or vLLM). It is omitted from the manifest when it equals the operator's
    default (ONNX) so existing deployments stay byte-equivalent. For vLLM,
    the operator's planner handles max_model_len, KV-cache size, and batch
    tuning automatically — this sample intentionally does not pin those.
    """
    preset = MODEL_PRESETS.get(model_name, {})
    workload_type = preset.get("workloadType", "generative")
    resources = preset.get("resources", {
        "requests": {"cpu": "2", "memory": "8Gi"},
        "limits": {"cpu": "4", "memory": "24Gi"},
    })

    manifest = {
        "apiVersion": f"{FOUNDRY_API_GROUP}/{FOUNDRY_API_VERSION}",
        "kind": "ModelDeployment",
        "metadata": {
            "name": deployment_name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": deployment_name,
                "app.kubernetes.io/component": "inference",
                "foundry.azure.com/hardware": compute,
            },
        },
        "spec": {
            "displayName": f"{model_name} ({compute.upper()})",
            "model": {
                "catalog": {
                    "name": model_name,
                    "version": model_version,
                },
            },
            "workloadType": workload_type,
            "compute": compute,
            "replicas": 1,
            "resources": resources,
            "port": 5000,
        },
    }

    # Translate the user-facing runtime token ('onnx', 'vllm') to the
    # operator's wire value. For the default ONNX path the wire value is
    # None — omit spec.runtime entirely so the CRD applies its own default
    # ('onnx-genai') and existing deployments stay byte-equivalent.
    wire_runtime = RUNTIME_WIRE_VALUE.get((runtime or "").lower())
    if wire_runtime is not None:
        manifest["spec"]["runtime"] = wire_runtime

    # GPU deployments need nodeSelector (docs: Quick Start GPU example)
    if compute == "gpu":
        node_selector = preset.get("nodeSelector", {})
        if node_selector:
            manifest["spec"]["nodeSelector"] = node_selector

    return manifest


def deploy_model(
    k8s_custom: client.CustomObjectsApi,
    manifest: dict,
    namespace: str,
    model_name: str,
    model_version: str,
    compute: str,
    runtime: str = DEFAULT_RUNTIME,
) -> tuple[dict, bool]:
    """Create the ModelDeployment custom resource.

    Returns (resource, created) — created is False when reusing an existing
    deployment that matches the requested model/version/compute/runtime.

    Uses inline catalog reference — the operator creates the Model CR
    automatically via lazy registration (docs: "Lazy Model Registration").
    """
    try:
        result = k8s_custom.create_namespaced_custom_object(
            group=FOUNDRY_API_GROUP,
            version=FOUNDRY_API_VERSION,
            namespace=namespace,
            plural=FOUNDRY_PLURAL,
            body=manifest,
        )
        print(f"  ✓ ModelDeployment '{result['metadata']['name']}' created")
        return result, True
    except ApiException as e:
        if e.status == 409:
            name = manifest["metadata"]["name"]
            existing = k8s_custom.get_namespaced_custom_object(
                group=FOUNDRY_API_GROUP,
                version=FOUNDRY_API_VERSION,
                namespace=namespace,
                plural=FOUNDRY_PLURAL,
                name=name,
            )

            # Validate that the existing deployment matches what was requested
            existing_spec = existing.get("spec", {})
            existing_catalog = existing_spec.get("model", {}).get("catalog", {})
            existing_model = existing_catalog.get("name", "")
            existing_version = existing_catalog.get("version", "")
            existing_compute = existing_spec.get("compute", "")
            existing_runtime_wire = (existing_spec.get("runtime") or "").lower()
            # Normalize wire value → user token for comparison. The CRD
            # default is 'onnx-genai' when the field is unset.
            existing_runtime = DEFAULT_RUNTIME
            for user_token, wire in RUNTIME_WIRE_VALUE.items():
                if wire is not None and existing_runtime_wire == wire:
                    existing_runtime = user_token
                    break
            requested_runtime = (runtime or DEFAULT_RUNTIME).lower()

            if (existing_model != model_name
                    or existing_version != model_version
                    or existing_compute != compute
                    or existing_runtime != requested_runtime):
                raise SampleError(
                    f"ModelDeployment '{name}' already exists but with a different configuration:\n"
                    f"    Existing: model={existing_model}, version={existing_version}, "
                    f"compute={existing_compute}, runtime={existing_runtime}\n"
                    f"    Requested: model={model_name}, version={model_version}, "
                    f"compute={compute}, runtime={requested_runtime}\n"
                    f"    To fix: delete the existing deployment first:\n"
                    f"      kubectl delete mdep {name} -n {namespace}\n"
                    f"    Or use a different --deployment-name."
                )

            print(f"  ⚠ ModelDeployment '{name}' already exists with matching config — reusing it")
            return existing, False
        raise


# ---------------------------------------------------------------------------
# Step 3 — Wait for the Deployment to Become Ready
# Docs: "Resource Lifecycle" states table
# ---------------------------------------------------------------------------


def wait_for_ready(
    k8s_custom: client.CustomObjectsApi,
    name: str,
    namespace: str,
    timeout_seconds: int = 600,
    poll_interval: int = 10,
):
    """Poll the ModelDeployment until state=Running and deploymentReady=true.

    Fail fast on Error state. The model image is downloaded on first deploy,
    so Creating → Running can take several minutes depending on model size
    and network speed (docs: Quick Start note).
    """
    print(f"  Waiting up to {timeout_seconds}s for '{name}' to reach Running state...")
    print(f"  (Model image is downloaded on first deploy — this may take a few minutes)\n")

    start = time.time()
    last_state = ""

    while time.time() - start < timeout_seconds:
        mdep = k8s_custom.get_namespaced_custom_object(
            group=FOUNDRY_API_GROUP,
            version=FOUNDRY_API_VERSION,
            namespace=namespace,
            plural=FOUNDRY_PLURAL,
            name=name,
        )

        status = mdep.get("status", {})
        state = status.get("state", STATE_PENDING)
        message = status.get("message", "")
        ready_replicas = status.get("readyReplicas", 0)
        deployment_ready = status.get("deploymentReady", False)

        if state != last_state:
            elapsed = int(time.time() - start)
            print(f"  [{elapsed:>4}s] State: {state}"
                  + (f" — {message}" if message else "")
                  + (f" (ready: {ready_replicas})" if ready_replicas else ""))
            last_state = state

        # Fail fast on Error (docs: check the message for error details)
        if state == STATE_ERROR:
            raise SampleError(
                f"Deployment entered Error state: {message}\n"
                f"    Troubleshooting: kubectl describe mdep {name} -n {namespace}"
            )

        # Success: Running + Ready (docs: "Wait for State=Running and Ready=true")
        if state == STATE_RUNNING and deployment_ready:
            internal_endpoint = status.get("internalEndpoint", "")
            print(f"\n  ✓ Deployment '{name}' is running and ready!")
            if internal_endpoint:
                print(f"  Internal endpoint: {internal_endpoint}")
            return mdep

        time.sleep(poll_interval)

    raise SampleError(
        f"Timed out after {timeout_seconds}s. Current state: {last_state}\n"
        f"    Check status: kubectl describe mdep {name} -n {namespace}"
    )


# ---------------------------------------------------------------------------
# Step 4 — Run Inference
# Docs: "Authentication" + "Run Inference" sections
# ---------------------------------------------------------------------------


def get_api_key(k8s_core: client.CoreV1Api, deployment_name: str,
                namespace: str) -> str:
    """Retrieve the primary API key from the auto-generated Secret.

    Docs: "API Key Generation and Storage" — the operator creates a Secret
    named '<deployment-name>-api-keys' with 'primary-key' and 'secondary-key'.
    """
    secret_name = f"{deployment_name}-api-keys"
    try:
        secret = k8s_core.read_namespaced_secret(secret_name, namespace)
    except ApiException as e:
        if e.status == 404:
            raise SampleError(
                f"Secret '{secret_name}' not found.\n"
                "    The deployment may not be fully ready yet."
            )
        if e.status == 403:
            raise SampleError(
                f"Access denied reading Secret '{secret_name}'.\n"
                "    Your RBAC role may not include Secret read permissions."
            )
        raise

    encoded = (secret.data or {}).get("primary-key", "")
    if not encoded:
        raise SampleError(
            f"Secret '{secret_name}' exists but 'primary-key' is missing.\n"
            "    The deployment may still be initializing."
        )

    api_key = base64.b64decode(encoded).decode("utf-8")
    print(f"  ✓ Retrieved API key from Secret '{secret_name}'")
    return api_key


def run_inference(
    endpoint: str,
    api_key: str,
    model_id: str,
    prompt: str = "What is the capital of France? Reply in one sentence.",
    insecure: bool = False,
):
    """Call the OpenAI-compatible chat completions endpoint.

    Docs: "Run Inference > Step 2 – Call the Inference Endpoint"
    Uses the same request format as the curl examples in the docs.

    Endpoint format (without ingress):
      https://<deployment-name>.foundry-local-operator.svc.cluster.local:5000
    With port-forward:
      https://localhost:5000

    Auth: 'Authorization: Bearer <API_KEY>' (docs: "Using API Keys in Requests")
    """
    url = f"{endpoint.rstrip('/')}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Request body matches the docs' inference examples exactly
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 256,
    }

    print(f"  Endpoint : {url}")
    print(f"  Model    : {model_id}")
    print(f"  Prompt   : {prompt}\n")

    # Disable SSL verification only when --insecure is set (self-signed certs).
    # The official docs use `curl -k` for internal endpoints.
    verify_tls = not insecure
    if insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        resp = requests.post(url, headers=headers, json=payload,
                             verify=verify_tls, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise SampleError(
            "Could not connect to the inference endpoint.\n"
            "    If running outside the cluster, set up port-forwarding:\n"
            f"      kubectl port-forward svc/<deployment-name> 5000:5000 "
            f"-n {FOUNDRY_NAMESPACE}\n"
            "    Then re-run with: --endpoint https://localhost:5000 --insecure"
        )
    except requests.exceptions.SSLError:
        raise SampleError(
            "SSL certificate verification failed.\n"
            "    Foundry Local uses self-signed certificates internally.\n"
            "    Re-run with --insecure to skip TLS verification."
        )
    except requests.exceptions.HTTPError:
        if resp.status_code == 401:
            raise SampleError(
                "Authentication failed (401 Unauthorized).\n"
                "    Verify the API key is correct.\n"
                "    Docs: Authentication > Using API Keys in Requests"
            )
        raise SampleError(f"HTTP {resp.status_code}: {resp.text}")

    result = resp.json()

    # Display response (matching docs' "Expected Response" format)
    print("  Response:")
    print(f"  {'-'*50}")
    choices = result.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        finish = choices[0].get("finish_reason", "")
        print(f"  {content}")
        print(f"  {'-'*50}")
        print(f"  finish_reason: {finish}")
    else:
        print(f"  {json.dumps(result, indent=2)}")

    return result


# ---------------------------------------------------------------------------
# Step 5 — Clean Up
# ---------------------------------------------------------------------------


def delete_deployment(k8s_custom: client.CustomObjectsApi, name: str,
                      namespace: str):
    """Delete the ModelDeployment custom resource."""
    try:
        k8s_custom.delete_namespaced_custom_object(
            group=FOUNDRY_API_GROUP,
            version=FOUNDRY_API_VERSION,
            namespace=namespace,
            plural=FOUNDRY_PLURAL,
            name=name,
        )
        print(f"  ✓ ModelDeployment '{name}' deleted")
    except ApiException as e:
        if e.status == 404:
            print(f"  ⚠ ModelDeployment '{name}' was already deleted")
        else:
            raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Foundry Local on Azure Local — Model Catalog Sample",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python catalog_sample.py                              # Phi-4 CPU (default)
  python catalog_sample.py --model Phi-4-generic-gpu --compute gpu
  python catalog_sample.py --catalog-only               # List catalog only
  python catalog_sample.py --skip-cleanup               # Keep deployment running

  # Two-step flow (running from your laptop):
  python catalog_sample.py --deploy-only                # Step A: deploy and exit
  # Then in another terminal: kubectl port-forward svc/<name> 5000:5000 -n foundry-local-operator
  python catalog_sample.py --infer-only --endpoint https://localhost:5000 --insecure
""",
    )
    parser.add_argument("--model", default="Phi-4-generic-cpu",
                        help="Catalog model name (default: Phi-4-generic-cpu)")
    parser.add_argument("--version", default=None,
                        help="Catalog model version (default: auto-detect from catalog)")
    parser.add_argument("--compute", choices=["cpu", "gpu"], default="cpu",
                        help="Compute type (default: cpu)")
    parser.add_argument("--runtime", choices=list(RUNTIME_CHOICES),
                        default=DEFAULT_RUNTIME,
                        help=f"Inference runtime (default: {DEFAULT_RUNTIME}). "
                             f"'{RUNTIME_VLLM}' requires --compute gpu.")
    parser.add_argument("--deployment-name", default=None,
                        help="Deployment name (default: derived from model name)")
    parser.add_argument("--namespace", default=FOUNDRY_NAMESPACE,
                        help=f"Kubernetes namespace (default: {FOUNDRY_NAMESPACE})")
    parser.add_argument("--endpoint", default=None,
                        help="Inference endpoint URL (e.g. https://localhost:5000). "
                             "Required when running outside the cluster.")
    parser.add_argument("--prompt", default="What is the capital of France? Reply in one sentence.",
                        help="Prompt to send to the model")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Deployment readiness timeout in seconds (default: 600)")
    parser.add_argument("--catalog-only", action="store_true",
                        help="Only query and display the catalog, then exit")
    parser.add_argument("--deploy-only", action="store_true",
                        help="Deploy the model and exit (skip inference). "
                             "Useful for setting up port-forwarding before inference.")
    parser.add_argument("--infer-only", action="store_true",
                        help="Skip deployment, run inference against an existing deployment. "
                             "Requires --endpoint if running outside the cluster.")
    parser.add_argument("--skip-cleanup", action="store_true",
                        help="Do not delete the deployment after inference")
    parser.add_argument("--insecure", action="store_true",
                        help="Skip TLS certificate verification (for self-signed certs)")

    args = parser.parse_args()

    # Validate flag combinations
    if args.deploy_only and args.infer_only:
        parser.error("--deploy-only and --infer-only are mutually exclusive")
    if args.catalog_only and (args.deploy_only or args.infer_only):
        parser.error("--catalog-only cannot be combined with --deploy-only or --infer-only")

    # vLLM requires GPU — validated up front so the user gets a clear error
    # before any cluster calls are made (docs: "vLLM Runtime > Requirements").
    if args.runtime == RUNTIME_VLLM and args.compute != "gpu":
        raise SampleError(
            f"--runtime {RUNTIME_VLLM} requires --compute gpu.\n"
            f"    The vLLM runtime is GPU-only on Foundry Local.\n"
            f"    Re-run with: --runtime {RUNTIME_VLLM} --compute gpu"
        )

    return args


def main():
    args = parse_args()
    namespace = args.namespace

    # Determine step count based on mode
    if args.catalog_only:
        total_steps = 2
    elif args.deploy_only:
        total_steps = 3
    elif args.infer_only:
        total_steps = 2
    else:
        total_steps = 5

    print("\n" + "=" * 60)
    print("  Foundry Local on Azure Local — Model Catalog Sample")
    print("=" * 60)

    # --- Load kubeconfig ---
    try:
        config.load_incluster_config()
        print("\n  Using in-cluster Kubernetes config")
    except config.ConfigException:
        try:
            config.load_kube_config()
            print("\n  Using kubeconfig from local environment")
        except Exception as exc:
            print(f"\n  ✗ Could not load Kubernetes config: {exc}")
            print("    Ensure kubectl is configured and can reach your cluster.")
            print("    Try: kubectl cluster-info")
            sys.exit(1)

    k8s_core = client.CoreV1Api()
    k8s_custom = client.CustomObjectsApi()
    k8s_ext = client.ApiextensionsV1Api()

    print_context_info(namespace)

    # --- Preflight checks ---
    check_crd_exists(k8s_ext)

    # --- State for signal handler cleanup ---
    cleanup_state = {"deployment_name": None, "namespace": namespace,
                     "k8s_custom": k8s_custom, "should_cleanup": False}

    def sigint_handler(signum, frame):
        name = cleanup_state["deployment_name"]
        if cleanup_state["should_cleanup"] and name:
            print(f"\n\n  ⚠ Interrupted — cleaning up deployment '{name}'...")
            try:
                delete_deployment(cleanup_state["k8s_custom"], name,
                                  cleanup_state["namespace"])
            except Exception:
                print(f"    ⚠ Cleanup failed. Manual cleanup:\n"
                      f"      kubectl delete mdep {name} -n {cleanup_state['namespace']}")
        else:
            print("\n\n  Interrupted by user.")
        sys.exit(130)

    signal.signal(signal.SIGINT, sigint_handler)

    # ===============================================================
    # --infer-only: skip catalog query and deployment, go to inference
    # ===============================================================
    if args.infer_only:
        deployment_name = args.deployment_name or dns_safe(args.model)

        # Resolve model_id: if version is specified, use it directly;
        # otherwise query the catalog to auto-detect. The inference model
        # id format depends on the runtime (see _inference_model_id):
        # vLLM uses the bare alias, ONNX uses '<name>:<version>'.
        if args.version is not None:
            full_model_id = f"{args.model}:{args.version}"
            inference_id = _inference_model_id(full_model_id, args.model, args.runtime)
        else:
            models = query_catalog(k8s_core, namespace)
            variant = resolve_variant(models, args.model, None,
                                       args.compute, runtime=args.runtime)
            if variant:
                inference_id = variant["inference_model_id"]
            else:
                raise SampleError(
                    f"Model '{args.model}' with compute='{args.compute}', "
                    f"runtime='{args.runtime}' not found in the catalog.\n"
                    "    Specify --version explicitly, or check --catalog-only output."
                )

        print_step(1, total_steps, "Run Inference")

        api_key = get_api_key(k8s_core, deployment_name, namespace)

        if args.endpoint:
            endpoint = args.endpoint
        else:
            endpoint = f"https://{deployment_name}.{namespace}.svc.cluster.local:5000"

        run_inference(
            endpoint=endpoint,
            api_key=api_key,
            model_id=inference_id,
            prompt=args.prompt,
            insecure=args.insecure,
        )

        print_step(2, total_steps, "Done")
        print(f"  Deployment '{deployment_name}' is still running.")
        print(f"  To delete: kubectl delete mdep {deployment_name} -n {namespace}")

        print(f"\n{'='*60}")
        print("  Sample completed successfully!")
        print(f"{'='*60}\n")
        return

    # ===============================================================
    # Standard flow: catalog → deploy → wait → infer → cleanup
    # ===============================================================

    # ---------------------------------------------------------------
    # Step 1 — Query the Model Catalog
    # ---------------------------------------------------------------
    print_step(1, total_steps, "Query the Model Catalog")

    models = query_catalog(k8s_core, namespace)
    display_catalog(models)

    if args.catalog_only:
        print("\n  Done (--catalog-only). No deployment created.\n")
        return

    # Resolve the requested model variant
    variant = resolve_variant(models, args.model, args.version, args.compute,
                              runtime=args.runtime)
    if not variant:
        version_str = f":{args.version}" if args.version else ""
        raise SampleError(
            f"Model '{args.model}{version_str}' with compute='{args.compute}', "
            f"runtime='{args.runtime}' not found in the catalog.\n"
            "    Available models are listed above. Check the MODEL_ID and RUNTIME columns.\n"
            "    If the model was recently added, trigger a manual catalog sync:\n"
            f"      kubectl create job --from=cronjob/foundry-local-catalog-sync "
            f"manual-sync -n {namespace}"
        )

    # Extract the resolved version from the model_id (format: "Name:Version")
    resolved_version = variant["model_id"].rsplit(":", 1)[-1]

    print(f"\n  Selected model:")
    print(f"    Alias     : {variant['alias']}")
    print(f"    Model ID  : {variant['model_id']}")
    print(f"    Compute   : {variant['compute'].upper()}")
    print(f"    Runtime   : {variant['runtime']}")
    print(f"    Size      : {variant['fileSizeBytes'] / (1024**3):.2f} GB")

    # ---------------------------------------------------------------
    # Step 2 — Deploy a Model from the Catalog
    # ---------------------------------------------------------------
    print_step(2, total_steps, "Deploy a Model from the Catalog")

    deployment_name = args.deployment_name or dns_safe(args.model)
    manifest = build_deployment_manifest(
        deployment_name=deployment_name,
        model_name=args.model,
        model_version=resolved_version,
        compute=args.compute,
        namespace=namespace,
        runtime=args.runtime,
    )

    # Show the manifest (users can copy it for their own deployments)
    print("  Manifest to apply:")
    print(f"  {'-'*50}")
    print(f"  apiVersion: {FOUNDRY_API_GROUP}/{FOUNDRY_API_VERSION}")
    print(f"  kind: ModelDeployment")
    print(f"  name: {deployment_name}")
    print(f"  model.catalog.name: {args.model}")
    print(f"  model.catalog.version: {resolved_version}")
    print(f"  workloadType: {manifest['spec']['workloadType']}")
    print(f"  compute: {args.compute}")
    if "runtime" in manifest["spec"]:
        print(f"  runtime: {manifest['spec']['runtime']} (user-token: {args.runtime})")
    else:
        print(f"  runtime: (CRD default — onnx-genai)")
    print(f"  port: 5000")
    print(f"  {'-'*50}\n")

    mdep_resource, was_created = deploy_model(
        k8s_custom, manifest, namespace,
        model_name=args.model,
        model_version=resolved_version,
        compute=args.compute,
        runtime=args.runtime,
    )

    # Track whether we should clean up on failure (only if we created it)
    should_cleanup = was_created and not args.skip_cleanup
    cleanup_state["deployment_name"] = deployment_name
    cleanup_state["should_cleanup"] = should_cleanup

    try:
        # ---------------------------------------------------------------
        # Step 3 — Wait for the Deployment to Become Ready
        # ---------------------------------------------------------------
        print_step(3, total_steps, "Wait for Deployment to Become Ready")

        mdep = wait_for_ready(k8s_custom, deployment_name, namespace,
                              timeout_seconds=args.timeout)

        # --deploy-only: stop here
        if args.deploy_only:
            print(f"\n  Done (--deploy-only). Deployment '{deployment_name}' is running.")
            print(f"\n  Next steps:")
            print(f"    1. Set up port-forwarding:")
            print(f"       kubectl port-forward svc/{deployment_name} 5000:5000 -n {namespace}")
            print(f"    2. Run inference:")
            print(f"       python catalog_sample.py --infer-only "
                  f"--endpoint https://localhost:5000 --insecure")
            cleanup_state["should_cleanup"] = False
            return

        # ---------------------------------------------------------------
        # Step 4 — Run Inference
        # ---------------------------------------------------------------
        print_step(4, total_steps, "Run Inference")

        api_key = get_api_key(k8s_core, deployment_name, namespace)

        # Determine the inference endpoint
        if args.endpoint:
            endpoint = args.endpoint
        else:
            # In-cluster service DNS
            endpoint = f"https://{deployment_name}.{namespace}.svc.cluster.local:5000"
            print(f"\n  ℹ No --endpoint specified. Using in-cluster DNS:")
            print(f"    {endpoint}")
            print(f"\n  If running from your workstation, use the two-step flow instead:")
            print(f"    python catalog_sample.py --deploy-only")
            print(f"    kubectl port-forward svc/{deployment_name} 5000:5000 -n {namespace}")
            print(f"    python catalog_sample.py --infer-only "
                  f"--endpoint https://localhost:5000 --insecure\n")

        run_inference(
            endpoint=endpoint,
            api_key=api_key,
            model_id=variant["inference_model_id"],
            prompt=args.prompt,
            insecure=args.insecure,
        )

    except Exception:
        # Guarantee cleanup on failure if we created the deployment
        if should_cleanup:
            print(f"\n  ⚠ Error occurred — cleaning up deployment '{deployment_name}'...")
            try:
                delete_deployment(k8s_custom, deployment_name, namespace)
            except Exception:
                print(f"    ⚠ Cleanup failed. Manual cleanup:\n"
                      f"      kubectl delete mdep {deployment_name} -n {namespace}")
        raise

    # ---------------------------------------------------------------
    # Step 5 — Clean Up
    # ---------------------------------------------------------------
    if not args.skip_cleanup and was_created:
        print_step(5, total_steps, "Clean Up")
        delete_deployment(k8s_custom, deployment_name, namespace)
    elif not was_created:
        print(f"\n  Skipping cleanup — deployment '{deployment_name}' existed before this run.")
        print(f"  To delete manually: kubectl delete mdep {deployment_name} -n {namespace}")
    else:
        print(f"\n  Skipping cleanup (--skip-cleanup). Deployment '{deployment_name}' "
              "is still running.")
        print(f"  To delete later: kubectl delete mdep {deployment_name} -n {namespace}")

    # Disable signal handler cleanup since we completed successfully
    cleanup_state["should_cleanup"] = False

    print(f"\n{'='*60}")
    print("  Sample completed successfully!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        main()
    except SampleError as e:
        print(f"\n  ✗ {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        # Fallback — signal handler should catch this first
        print("\n\n  Interrupted by user.\n")
        sys.exit(130)
