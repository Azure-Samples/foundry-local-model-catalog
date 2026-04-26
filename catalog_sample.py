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
  python catalog_sample.py --model Phi-4-cuda-gpu --version 1 --compute gpu

  # Query the catalog only (no deployment)
  python catalog_sample.py --catalog-only

  # Skip cleanup (leave deployment running)
  python catalog_sample.py --skip-cleanup

Documentation:
  https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local

See Also:
  - Inference Operator overview and CRD reference
  - Model Catalog > ConfigMap Format and Structure
  - Authentication > API Key Generation and Storage
"""

import argparse
import base64
import json
import re
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

# Resource presets per sample model (docs: Quick Start YAML examples)
MODEL_PRESETS = {
    "Phi-4-generic-cpu": {
        "compute": "cpu",
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "2", "memory": "8Gi"},
            "limits": {"cpu": "4", "memory": "24Gi"},
        },
    },
    "Phi-4-cuda-gpu": {
        "compute": "gpu",
        "workloadType": "generative",
        "resources": {
            "requests": {"cpu": "4", "memory": "32Gi"},
            "limits": {"cpu": "8", "memory": "64Gi", "gpu": 1},
        },
        "nodeSelector": {"foundry/workload": "gpu"},
    },
}


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


def print_context_info(k8s_core: client.CoreV1Api):
    """Print the current Kubernetes context so users know which cluster
    will be modified. Docs: always verify your kubeconfig before mutating."""
    try:
        _, active_context = config.list_kube_config_contexts()
        ctx = active_context.get("name", "unknown")
        cluster = active_context.get("context", {}).get("cluster", "unknown")
        print(f"  Kubernetes context : {ctx}")
        print(f"  Cluster            : {cluster}")
        print(f"  Target namespace   : {FOUNDRY_NAMESPACE}")
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
            print(f"  ✗ CRD '{crd_name}' not found.")
            print("    Is the Inference Operator installed?")
            print("    See docs: Quick Start > Step 2 – Install Inference Operator")
            sys.exit(1)
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
            print(f"  ✗ ConfigMap '{CATALOG_CONFIGMAP}' not found in '{namespace}'.")
            print("    The catalog may not have synced yet.")
            print("    Try: kubectl create job --from=cronjob/foundry-local-catalog-sync manual-sync "
                  f"-n {namespace}")
            sys.exit(1)
        raise

    raw = cm.data.get("catalog.json")
    if not raw:
        print("  ✗ ConfigMap exists but 'catalog.json' key is empty.")
        sys.exit(1)

    catalog = json.loads(raw)
    models = catalog.get("models", [])

    last_sync = ""
    if cm.metadata.annotations:
        last_sync = cm.metadata.annotations.get("foundry.azure.com/last-sync", "")

    print(f"  Catalog version : {catalog.get('version', 'N/A')}")
    print(f"  Last sync       : {last_sync or 'N/A'}")
    print(f"  Total models    : {catalog.get('total', len(models))}")

    return models


def display_catalog(models: list[dict]):
    """Display the catalog in a table matching the docs' expected output format."""
    rows = []
    for m in models:
        for v in m.get("variants", []):
            size_gb = round(v.get("fileSizeBytes", 0) / (1024**3), 2)
            rows.append([
                m.get("alias", ""),
                v.get("compute", "").upper(),
                f"{size_gb}GB",
                v.get("id", ""),
            ])

    print(tabulate(rows, headers=["ALIAS", "DEVICE", "SIZE", "MODEL_ID"],
                   tablefmt="simple"))


def resolve_variant(models: list[dict], model_name: str, version: str,
                    compute: str) -> dict | None:
    """Find a specific variant matching the model name, version, and compute type.

    Avoids the brittle variants[0] assumption — explicitly matches compute type.
    """
    target_id = f"{model_name}:{version}"

    for m in models:
        for v in m.get("variants", []):
            if v.get("id") == target_id and v.get("compute", "").lower() == compute.lower():
                return {
                    "alias": m.get("alias", ""),
                    "model_id": v["id"],
                    "compute": v.get("compute", ""),
                    "displayName": m.get("displayName", ""),
                    "task": m.get("task", ""),
                    "fileSizeBytes": v.get("fileSizeBytes", 0),
                }

    # Fallback: match by model name prefix in variant ID
    for m in models:
        for v in m.get("variants", []):
            vid = v.get("id", "")
            if vid.startswith(model_name) and v.get("compute", "").lower() == compute.lower():
                return {
                    "alias": m.get("alias", ""),
                    "model_id": vid,
                    "compute": v.get("compute", ""),
                    "displayName": m.get("displayName", ""),
                    "task": m.get("task", ""),
                    "fileSizeBytes": v.get("fileSizeBytes", 0),
                }

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
) -> dict:
    """Build a ModelDeployment manifest grounded to the official YAML schema.

    Docs reference: "ModelDeployment Reference > Spec Fields" table.
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
                f"foundry.azure.com/hardware": compute,
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
        },
    }

    # GPU deployments need nodeSelector (docs: Quick Start GPU example)
    if compute == "gpu":
        node_selector = preset.get("nodeSelector", {})
        if node_selector:
            manifest["spec"]["nodeSelector"] = node_selector

        # GPU resource limit (docs: "Configure GPU Workloads")
        gpu_limit = resources.get("limits", {}).get("gpu")
        if gpu_limit:
            manifest["spec"]["resources"]["limits"]["nvidia.com/gpu"] = gpu_limit

    return manifest


def deploy_model(
    k8s_custom: client.CustomObjectsApi,
    manifest: dict,
    namespace: str,
) -> dict:
    """Create the ModelDeployment custom resource.

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
        return result
    except ApiException as e:
        if e.status == 409:
            name = manifest["metadata"]["name"]
            print(f"  ⚠ ModelDeployment '{name}' already exists — reusing it")
            return k8s_custom.get_namespaced_custom_object(
                group=FOUNDRY_API_GROUP,
                version=FOUNDRY_API_VERSION,
                namespace=namespace,
                plural=FOUNDRY_PLURAL,
                name=name,
            )
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
            print(f"\n  ✗ Deployment entered Error state: {message}")
            print("    Troubleshooting: kubectl describe mdep "
                  f"{name} -n {namespace}")
            sys.exit(1)

        # Success: Running + Ready (docs: "Wait for State=Running and Ready=true")
        if state == STATE_RUNNING and deployment_ready:
            internal_endpoint = status.get("internalEndpoint", "")
            print(f"\n  ✓ Deployment '{name}' is running and ready!")
            if internal_endpoint:
                print(f"  Internal endpoint: {internal_endpoint}")
            return mdep

        time.sleep(poll_interval)

    print(f"\n  ✗ Timed out after {timeout_seconds}s. Current state: {last_state}")
    print(f"    Check status: kubectl describe mdep {name} -n {namespace}")
    sys.exit(1)


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
            print(f"  ✗ Secret '{secret_name}' not found.")
            print("    The deployment may not be fully ready yet.")
            sys.exit(1)
        if e.status == 403:
            print(f"  ✗ Access denied reading Secret '{secret_name}'.")
            print("    Your RBAC role may not include Secret read permissions.")
            sys.exit(1)
        raise

    encoded = secret.data.get("primary-key", "")
    api_key = base64.b64decode(encoded).decode("utf-8")
    print(f"  ✓ Retrieved API key from Secret '{secret_name}'")
    return api_key


def run_inference(
    endpoint: str,
    api_key: str,
    model_id: str,
    prompt: str = "What is the capital of France? Reply in one sentence.",
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

    # Disable SSL verification for self-signed certs (docs: internal CA
    # uses self-signed certificates — "-k flag (curl)" is used in examples)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        resp = requests.post(url, headers=headers, json=payload,
                             verify=False, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("  ✗ Could not connect to the inference endpoint.")
        print("    If running outside the cluster, set up port-forwarding:")
        print(f"      kubectl port-forward svc/<deployment-name> 5000:5000 "
              f"-n {FOUNDRY_NAMESPACE}")
        print("    Then set: --endpoint https://localhost:5000")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            print("  ✗ Authentication failed (401 Unauthorized).")
            print("    Verify the API key is correct.")
            print("    Docs: Authentication > Using API Keys in Requests")
        else:
            print(f"  ✗ HTTP {resp.status_code}: {resp.text}")
        sys.exit(1)

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
  python catalog_sample.py --model Phi-4-cuda-gpu --compute gpu
  python catalog_sample.py --catalog-only               # List catalog only
  python catalog_sample.py --skip-cleanup               # Keep deployment running

Docs: https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local
""",
    )
    parser.add_argument("--model", default="Phi-4-generic-cpu",
                        help="Catalog model name (default: Phi-4-generic-cpu)")
    parser.add_argument("--version", default="1",
                        help="Catalog model version (default: 1)")
    parser.add_argument("--compute", choices=["cpu", "gpu"], default="cpu",
                        help="Compute type (default: cpu)")
    parser.add_argument("--deployment-name", default=None,
                        help="Deployment name (default: derived from model name)")
    parser.add_argument("--namespace", default=FOUNDRY_NAMESPACE,
                        help=f"Kubernetes namespace (default: {FOUNDRY_NAMESPACE})")
    parser.add_argument("--endpoint", default=None,
                        help="Inference endpoint URL override (e.g. https://localhost:5000)")
    parser.add_argument("--prompt", default="What is the capital of France? Reply in one sentence.",
                        help="Prompt to send to the model")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Deployment readiness timeout in seconds (default: 600)")
    parser.add_argument("--catalog-only", action="store_true",
                        help="Only query and display the catalog, then exit")
    parser.add_argument("--skip-cleanup", action="store_true",
                        help="Do not delete the deployment after inference")
    return parser.parse_args()


def main():
    args = parse_args()
    total_steps = 2 if args.catalog_only else 5
    namespace = args.namespace

    print("\n" + "=" * 60)
    print("  Foundry Local on Azure Local — Model Catalog Sample")
    print("=" * 60)

    # --- Load kubeconfig ---
    try:
        config.load_incluster_config()
        print("\n  Using in-cluster Kubernetes config")
    except config.ConfigException:
        config.load_kube_config()
        print("\n  Using kubeconfig from local environment")

    k8s_core = client.CoreV1Api()
    k8s_custom = client.CustomObjectsApi()
    k8s_ext = client.ApiextensionsV1Api()

    print_context_info(k8s_core)

    # --- Preflight checks ---
    check_crd_exists(k8s_ext)

    # ---------------------------------------------------------------
    # Step 1 — Query the Model Catalog
    # Docs: "Model Catalog > ConfigMap Format and Structure"
    # ---------------------------------------------------------------
    print_step(1, total_steps, "Query the Model Catalog")

    models = query_catalog(k8s_core, namespace)
    display_catalog(models)

    if args.catalog_only:
        print("\n  Done (--catalog-only). No deployment created.\n")
        return

    # Resolve the requested model variant
    variant = resolve_variant(models, args.model, args.version, args.compute)
    if not variant:
        print(f"\n  ✗ Model '{args.model}:{args.version}' with compute='{args.compute}' "
              "not found in the catalog.")
        print("    Available models are listed above. Check the MODEL_ID column.")
        print("    If the model was recently added, trigger a manual catalog sync:")
        print(f"      kubectl create job --from=cronjob/foundry-local-catalog-sync "
              f"manual-sync -n {namespace}")
        sys.exit(1)

    print(f"\n  Selected model:")
    print(f"    Alias     : {variant['alias']}")
    print(f"    Model ID  : {variant['model_id']}")
    print(f"    Compute   : {variant['compute'].upper()}")
    print(f"    Size      : {variant['fileSizeBytes'] / (1024**3):.2f} GB")

    # ---------------------------------------------------------------
    # Step 2 — Deploy a Model from the Catalog
    # Docs: "Deploying Models > Deploy from Catalog (Inline)"
    # ---------------------------------------------------------------
    print_step(2, total_steps, "Deploy a Model from the Catalog")

    deployment_name = args.deployment_name or dns_safe(args.model)
    manifest = build_deployment_manifest(
        deployment_name=deployment_name,
        model_name=args.model,
        model_version=args.version,
        compute=args.compute,
        namespace=namespace,
    )

    # Show the manifest (users can copy it for their own deployments)
    print("  Manifest to apply:")
    print(f"  {'-'*50}")
    print(f"  apiVersion: {FOUNDRY_API_GROUP}/{FOUNDRY_API_VERSION}")
    print(f"  kind: ModelDeployment")
    print(f"  name: {deployment_name}")
    print(f"  model.catalog.name: {args.model}")
    print(f"  model.catalog.version: {args.version}")
    print(f"  workloadType: {manifest['spec']['workloadType']}")
    print(f"  compute: {args.compute}")
    print(f"  {'-'*50}\n")

    deploy_model(k8s_custom, manifest, namespace)

    # ---------------------------------------------------------------
    # Step 3 — Wait for the Deployment to Become Ready
    # Docs: "Resource Lifecycle" — wait for State=Running, Ready=true
    # ---------------------------------------------------------------
    print_step(3, total_steps, "Wait for Deployment to Become Ready")

    mdep = wait_for_ready(k8s_custom, deployment_name, namespace,
                          timeout_seconds=args.timeout)

    # ---------------------------------------------------------------
    # Step 4 — Run Inference
    # Docs: "Authentication" + "Run Inference" sections
    # ---------------------------------------------------------------
    print_step(4, total_steps, "Run Inference")

    api_key = get_api_key(k8s_core, deployment_name, namespace)

    # Determine the inference endpoint
    if args.endpoint:
        endpoint = args.endpoint
    else:
        # Default: in-cluster service DNS (docs: "Getting the endpoint without ingress")
        # Format: https://<name>.foundry-local-operator.svc.cluster.local:5000
        endpoint = f"https://{deployment_name}.{namespace}.svc.cluster.local:5000"
        print(f"\n  Using in-cluster endpoint: {endpoint}")
        print(f"  If running outside the cluster, set up port-forwarding:")
        print(f"    kubectl port-forward svc/{deployment_name} 5000:5000 -n {namespace}")
        print(f"    Then re-run with: --endpoint https://localhost:5000\n")

    run_inference(
        endpoint=endpoint,
        api_key=api_key,
        model_id=variant["model_id"],
        prompt=args.prompt,
    )

    # ---------------------------------------------------------------
    # Step 5 — Clean Up
    # ---------------------------------------------------------------
    if not args.skip_cleanup:
        print_step(5, total_steps, "Clean Up")
        delete_deployment(k8s_custom, deployment_name, namespace)
    else:
        print(f"\n  Skipping cleanup (--skip-cleanup). Deployment '{deployment_name}' "
              "is still running.")
        print(f"  To delete later: kubectl delete mdep {deployment_name} -n {namespace}")

    print(f"\n{'='*60}")
    print("  Sample completed successfully!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
