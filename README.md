# Foundry Local on Azure Local — Model Catalog Sample

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

A Python code sample that demonstrates the **model catalog lifecycle** on Foundry Local on Azure Local. Walk through the complete flow — from querying available models to deploying one, running inference, and cleaning up — using the Kubernetes API.

## What This Sample Does

| Step | Action |
|------|--------|
| **1** | **Query the model catalog** — list all available models from the cluster's catalog ConfigMap |
| **2** | **Deploy a model** — create a `ModelDeployment` custom resource from a catalog entry |
| **3** | **Wait for ready** — poll until the deployment reaches `Running` + `Ready` state |
| **4** | **Run inference** — call the OpenAI-compatible `/v1/chat/completions` endpoint |
| **5** | **Clean up** — delete the deployment |

## Prerequisites

Before running this sample, ensure you have:

1. **A Kubernetes cluster with Foundry Local installed**
   - Azure Local with AKS or any Arc-connected Kubernetes cluster
   - The Foundry Local Inference Operator installed via Helm
   - cert-manager and trust-manager installed

2. **kubectl access** configured to the cluster (`kubeconfig`)
   - Required permissions: read ConfigMaps, read Secrets, read CRDs, and create/get/delete `modeldeployments.foundrylocal.azure.com` in the `foundry-local-operator` namespace

3. **Python 3.9+** with pip

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Azure-Samples/foundry-local-model-catalog.git
cd foundry-local-model-catalog
```

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Verify cluster access

```bash
# Confirm you can reach the cluster
kubectl get pods -n foundry-local-operator

# Verify the Inference Operator CRDs are installed
kubectl get crd | grep foundry
```

### 4. Run the sample

```bash
# Default: deploy Phi-4 on CPU, run inference, clean up
python catalog_sample.py
```

## Usage Examples

```bash
# List all available models in the catalog (no deployment)
python catalog_sample.py --catalog-only

# Deploy Phi-4 on GPU
python catalog_sample.py --model Phi-4-generic-gpu --compute gpu

# Deploy Phi-4-mini with the vLLM runtime on GPU
python catalog_sample.py --model Phi-4-mini-instruct --compute gpu --runtime vllm

# Deploy and keep the model running after inference
python catalog_sample.py --skip-cleanup

# Two-step flow (running from your laptop):
python catalog_sample.py --deploy-only                # Deploy and wait for ready
# In another terminal: kubectl port-forward svc/phi-4-generic-cpu 5000:5000 -n foundry-local-operator
python catalog_sample.py --infer-only --endpoint https://localhost:5000 --insecure

# Use a custom prompt
python catalog_sample.py --prompt "Explain quantum computing in two sentences."
```

### Choosing a runtime

Use ONNX-GenAI on CPU-only nodes, for compact models, or for single-application workloads. Use vLLM on GPU nodes for high-throughput, multi-user serving of larger models. Both runtimes expose the same OpenAI-compatible REST endpoint — your client code does not change.

### Running from Outside the Cluster

If you're running this script from your laptop (not from within the cluster), use the two-step flow:

```bash
# Step 1: Deploy the model and wait for it to become ready
python catalog_sample.py --deploy-only

# Step 2: In a separate terminal, set up port-forwarding
kubectl port-forward svc/phi-4-generic-cpu 5000:5000 -n foundry-local-operator

# Step 3: Run inference using the local endpoint
python catalog_sample.py --infer-only --endpoint https://localhost:5000 --insecure
```

> **Note:** Foundry Local uses self-signed TLS certificates internally. Use `--insecure` to skip TLS verification, matching the `-k` flag used in the official docs' curl examples. In production, configure proper TLS certificates.

## Clean Up

The sample deletes the deployed model automatically after inference. To keep the model running, use `--skip-cleanup`:

```bash
python catalog_sample.py --skip-cleanup
```

To manually delete a deployment later:

```bash
kubectl delete modeldeployment <deployment-name> -n foundry-local-operator
```

## Command-Line Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `Phi-4-generic-cpu` | Catalog model name |
| `--version` | *(auto-detect)* | Catalog model version |
| `--compute` | `cpu` | Compute type (`cpu` or `gpu`) |
| `--runtime` | `onnx` | Inference runtime (`onnx` or `vllm`). `vllm` requires `--compute gpu`. |
| `--deployment-name` | *(derived from model)* | Custom deployment name |
| `--namespace` | `foundry-local-operator` | Kubernetes namespace |
| `--endpoint` | *(in-cluster DNS)* | Inference endpoint URL (required when running outside the cluster) |
| `--prompt` | `"What is the capital of France? Reply in one sentence."` | Prompt to send |
| `--timeout` | `600` | Deployment readiness timeout (seconds) |
| `--catalog-only` | `false` | List catalog and exit |
| `--deploy-only` | `false` | Deploy the model and exit (skip inference) |
| `--infer-only` | `false` | Skip deployment, run inference against existing deployment |
| `--skip-cleanup` | `false` | Keep deployment running after inference |
| `--insecure` | `false` | Skip TLS certificate verification (for self-signed certs) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Workstation                          │
│                                                             │
│  catalog_sample.py                                          │
│    │                                                        │
│    ├─ kubernetes client ──► Kubernetes API Server            │
│    │   • Read ConfigMap (catalog)                           │
│    │   • Create/Watch ModelDeployment (CRD)                 │
│    │   • Read Secret (API key)                              │
│    │                                                        │
│    └─ requests (HTTP) ──► Model Inference Endpoint          │
│        • POST /v1/chat/completions                          │
│        • Auth: Bearer <API_KEY>                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Azure Local)                │
│                                                             │
│  foundry-local-operator namespace                           │
│    ├─ Inference Operator (watches CRDs)                     │
│    ├─ ConfigMap: foundry-local-catalog                      │
│    │   └─ catalog.json (synced from Azure AI Foundry)       │
│    ├─ ModelDeployment CR ──► Deployment + Service + Ingress │
│    ├─ Secret: <name>-api-keys (auto-generated)              │
│    └─ Model Pod (TLS sidecar + inference container)         │
└─────────────────────────────────────────────────────────────┘
```

## Using the OpenAI Python SDK

The inference endpoint is fully OpenAI-compatible. If you prefer to use the [OpenAI Python SDK](https://github.com/openai/openai-python) instead of raw HTTP calls, install the additional dependencies first:

```bash
pip install openai httpx
```

Then connect like this:

```python
import httpx
from openai import OpenAI

# After deploying the model and setting up port-forward:
#   kubectl port-forward svc/phi-4-generic-cpu 5000:5000 -n foundry-local-operator

client = OpenAI(
    base_url="https://localhost:5000/v1",
    api_key="<YOUR_API_KEY>",  # From: kubectl get secret phi-4-generic-cpu-api-keys ...
    http_client=httpx.Client(verify=False),  # Self-signed certs
)

response = client.chat.completions.create(
    model="Phi-4-generic-cpu:1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    max_tokens=256,
)

print(response.choices[0].message.content)
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Inference Operator** | K8s operator that manages AI model lifecycle |
| **Model Catalog** | ConfigMap caching model metadata from Azure AI Foundry |
| **ModelDeployment** | CRD that creates a running inference endpoint |
| **Lazy Registration** | Operator auto-creates Model CR from catalog on first deploy |
| **API Key Auth** | Auto-generated primary/secondary keys in K8s Secrets |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CRD not found` | Install the Inference Operator via Helm |
| `ConfigMap not found` | Trigger a catalog sync: `kubectl create job --from=cronjob/foundry-local-catalog-sync manual-sync -n foundry-local-operator` |
| `Deployment stuck in Creating` | Model image is downloading — check pod events: `kubectl describe mdep <name> -n foundry-local-operator` |
| `Deployment in Error state` | Check the error message: `kubectl describe mdep <name> -n foundry-local-operator` |
| `Connection refused on inference` | Set up port-forwarding: `kubectl port-forward svc/<name> 5000:5000 -n foundry-local-operator` |
| `401 Unauthorized` | Verify the API key: `kubectl get secret <name>-api-keys -n foundry-local-operator -o jsonpath='{.data.primary-key}' \| base64 -d` |

## Resources

- [Foundry Local (Windows)](https://github.com/microsoft/Foundry-Local)
- [Foundry Azure Local Chat Sample](https://github.com/Azure-Samples/foundry-azure-local-chat)
- [Microsoft AI Foundry](https://learn.microsoft.com/azure/ai-studio/)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a [Contributor License Agreement (CLA)](https://cla.opensource.microsoft.com) declaring that you have the right to, and actually do, grant us the rights to use your contribution.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License — see [LICENSE.md](LICENSE.md) for details.
