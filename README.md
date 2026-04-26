# Foundry Local on Azure Local — Model Catalog Sample

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

A Python code sample that demonstrates the **model catalog lifecycle** on [Foundry Local on Azure Local](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local). Walk through the complete flow — from querying available models to deploying one, running inference, and cleaning up — using the Kubernetes API.

## What This Sample Does

| Step | Action | Docs Reference |
|------|--------|----------------|
| **1** | **Query the model catalog** — list all available models from the cluster's catalog ConfigMap | [Model Catalog > ConfigMap Format](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#configmap-format-and-structure) |
| **2** | **Deploy a model** — create a `ModelDeployment` custom resource from a catalog entry | [Deploy from Catalog (Inline)](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#deploy-from-catalog-inline) |
| **3** | **Wait for ready** — poll until the deployment reaches `Running` + `Ready` state | [Resource Lifecycle](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#the-two-resource-model) |
| **4** | **Run inference** — call the OpenAI-compatible `/v1/chat/completions` endpoint | [Run Inference](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#run-inference) |
| **5** | **Clean up** — delete the deployment | — |

## Prerequisites

Before running this sample, ensure you have:

1. **A Kubernetes cluster with Foundry Local installed**
   - Azure Local with AKS or any Arc-connected Kubernetes cluster
   - The Foundry Local Inference Operator installed via Helm
   - cert-manager and trust-manager installed
   - See: [Quick Start](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#quick-start)

2. **kubectl access** configured to the cluster (`kubeconfig`)
   - Required permissions: read ConfigMaps, read Secrets, read CRDs, and create/get/delete `modeldeployments.foundrylocal.azure.com` in the `foundry-local-operator` namespace

3. **Python 3.9+** with pip

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Azure-Samples/foundry-azure-local-model-catalog.git
cd foundry-azure-local-model-catalog
```

### 2. Install dependencies

```bash
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
python catalog_sample.py --model Phi-4-cuda-gpu --version 1 --compute gpu

# Deploy and keep the model running after inference
python catalog_sample.py --skip-cleanup

# Use a custom prompt
python catalog_sample.py --prompt "Explain quantum computing in two sentences."

# Connect via port-forward (when running outside the cluster)
python catalog_sample.py --endpoint https://localhost:5000 --insecure
```

### Running from Outside the Cluster

If you're running this script from your laptop (not from within the cluster), you'll need to set up port-forwarding for the inference call:

```bash
# In a separate terminal, after the deployment is running:
kubectl port-forward svc/<deployment-name> 5000:5000 -n foundry-local-operator

# Then run the sample with the local endpoint:
python catalog_sample.py --endpoint https://localhost:5000 --insecure
```

> **Note:** Foundry Local uses self-signed TLS certificates internally. Use `--insecure` to skip TLS verification, matching the `-k` flag used in the [official docs' curl examples](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#step-2--call-the-inference-endpoint). In production, configure proper TLS certificates via the [TLS Configuration](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#tls-configuration) guide.

## Command-Line Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `Phi-4-generic-cpu` | Catalog model name |
| `--version` | `1` | Catalog model version |
| `--compute` | `cpu` | Compute type (`cpu` or `gpu`) |
| `--deployment-name` | *(derived from model)* | Custom deployment name |
| `--namespace` | `foundry-local-operator` | Kubernetes namespace |
| `--endpoint` | *(in-cluster DNS)* | Inference endpoint URL (required when running outside the cluster) |
| `--prompt` | `"What is the capital of France? Reply in one sentence."` | Prompt to send |
| `--timeout` | `600` | Deployment readiness timeout (seconds) |
| `--catalog-only` | `false` | List catalog and exit |
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

| Concept | Description | Docs |
|---------|-------------|------|
| **Inference Operator** | K8s operator that manages AI model lifecycle | [Overview](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#inference-operator) |
| **Model Catalog** | ConfigMap caching model metadata from Azure AI Foundry | [Model Catalog](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#model-catalog) |
| **ModelDeployment** | CRD that creates a running inference endpoint | [Deploying Models](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#deploying-models-modeldeployment) |
| **Lazy Registration** | Operator auto-creates Model CR from catalog on first deploy | [Lazy Registration](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#lazy-model-registration) |
| **API Key Auth** | Auto-generated primary/secondary keys in K8s Secrets | [Authentication](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#authentication) |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CRD not found` | Install the Inference Operator: [Step 2](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#step-2--install-inference-operator) |
| `ConfigMap not found` | Trigger a catalog sync: `kubectl create job --from=cronjob/foundry-local-catalog-sync manual-sync -n foundry-local-operator` |
| `Deployment stuck in Creating` | Model image is downloading — check pod events: `kubectl describe mdep <name> -n foundry-local-operator` |
| `Deployment in Error state` | Check the error message and [Troubleshooting guide](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local#troubleshooting) |
| `Connection refused on inference` | Set up port-forwarding: `kubectl port-forward svc/<name> 5000:5000 -n foundry-local-operator` |
| `401 Unauthorized` | Verify the API key: `kubectl get secret <name>-api-keys -n foundry-local-operator -o jsonpath='{.data.primary-key}' \| base64 -d` |

## Resources

- [Foundry Local on Azure Local Documentation](https://github.com/FoundryLocalOnAzureLocal/Foundry-Local-On-Azure-Local)
- [Foundry Local (Windows)](https://github.com/microsoft/Foundry-Local)
- [Foundry Azure Local Chat Sample](https://github.com/Azure-Samples/foundry-azure-local-chat)
- [Microsoft AI Foundry](https://learn.microsoft.com/azure/ai-studio/)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a [Contributor License Agreement (CLA)](https://cla.opensource.microsoft.com) declaring that you have the right to, and actually do, grant us the rights to use your contribution.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License — see [LICENSE.md](LICENSE.md) for details.
