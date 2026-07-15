# Foundry Local on Azure Local - Model Catalog

This document is a snapshot of the model catalog available on Foundry Local on Azure Local.

| Field | Value |
|-------|-------|
| **Snapshot date (UTC)** | 2026-07-14 |
| **Catalog version** | `2026-07-13T23:13:30.740367+00:00` |
| **Catalog last sync (UTC)** | `2026-07-13T23:13:25.471632+00:00` |
| **Total entries** | 173 |
| **ONNX entries** | 70 |
| **vLLM entries** | 103 |
| **Chat-completion models** | 151 |
| **Automatic-speech-recognition models** | 22 |

## Catalog Schema

Each row represents one runnable artifact: an ONNX variant for ONNX models, or a single vLLM entry per vLLM model.

| Field | Source | Notes |
|-------|--------|-------|
| **Alias** | `models[].alias` | Short, friendly name |
| **Display Name** | `models[].displayName` | Human-readable name |
| **Publisher** | `models[].publisher` | Model owner (e.g., Microsoft, OpenAI) |
| **Task** | `models[].task` | e.g., `chat-completion`, `automatic-speech-recognition` |
| **Framework** | `models[].framework` | Inference framework (`ONNX`, `vllm`) |
| **Compute** | `models[].variants[].compute` | `CPU` or `GPU` for ONNX variants; `—` for vLLM |
| **Execution Provider** | `models[].variants[].executionProvider` | ONNX execution provider (for example `CPUExecutionProvider`, `CUDAExecutionProvider`) |
| **Model ID** | `models[].variants[].id` or `models[].id` | Use this as `spec.model.catalog.name` in your `ModelDeployment` |

## Models

| Alias | Display Name | Publisher | Task | Framework | Compute | Execution Provider | Model ID |
|-------|--------------|-----------|------|-----------|---------|--------------------|----------|
| qwen2.5-coder-0.5b | qwen2.5-coder-0.5b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-coder-0.5b-instruct-generic-cpu:4 |
| phi-4-mini-reasoning | Phi-4-mini-reasoning-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-4-mini-reasoning-generic-cpu:3 |
| qwen2.5-0.5b | qwen2.5-0.5b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-0.5b-instruct-generic-cpu:4 |
| qwen2.5-1.5b | qwen2.5-1.5b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-1.5b-instruct-generic-cpu:4 |
| qwen2.5-coder-1.5b | qwen2.5-coder-1.5b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-coder-1.5b-instruct-generic-cpu:4 |
| phi-4-mini | Phi-4-mini-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-4-mini-instruct-generic-cpu:5 |
| qwen2.5-14b | qwen2.5-14b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-14b-instruct-generic-cpu:4 |
| qwen2.5-coder-14b | qwen2.5-coder-14b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-coder-14b-instruct-generic-cpu:4 |
| qwen2.5-coder-7b | qwen2.5-coder-7b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-coder-7b-instruct-generic-cpu:4 |
| qwen2.5-7b | qwen2.5-7b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen2.5-7b-instruct-generic-cpu:4 |
| gpt-oss-20b | gpt-oss-20b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | gpt-oss-20b-generic-cpu:1 |
| phi-3-mini-128k | Phi-3-mini-128k-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-3-mini-128k-instruct-generic-cpu:3 |
| phi-3.5-mini | Phi-3.5-mini-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-3.5-mini-instruct-generic-cpu:2 |
| phi-4 | Phi-4-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-4-generic-cpu:2 |
| deepseek-r1-7b | deepseek-r1-distill-qwen-7b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | deepseek-r1-distill-qwen-7b-generic-cpu:4 |
| phi-3-mini-4k | Phi-3-mini-4k-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | Phi-3-mini-4k-instruct-generic-cpu:3 |
| mistral-7b-v0.2 | mistralai-Mistral-7B-Instruct-v0-2-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | mistralai-Mistral-7B-Instruct-v0-2-generic-cpu:3 |
| deepseek-r1-14b | deepseek-r1-distill-qwen-14b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | deepseek-r1-distill-qwen-14b-generic-cpu:4 |
| qwen3-14b | qwen3-14b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3-14b-generic-cpu:2 |
| qwen3-1.7b | qwen3-1.7b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3-1.7b-generic-cpu:2 |
| qwen3-4b | qwen3-4b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3-4b-generic-cpu:3 |
| qwen3-0.6b | qwen3-0.6b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3-0.6b-generic-cpu:4 |
| qwen3-8b | qwen3-8b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3-8b-generic-cpu:2 |
| nemotron-speech-streaming-en-0.6b | nemotron-speech-streaming-en-0.6b-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | nemotron-speech-streaming-en-0.6b-generic-cpu:3 |
| nemotron-speech-streaming-es-0.6b | nemotron-speech-streaming-es-0.6b-ft-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | nemotron-speech-streaming-es-0.6b-ft-generic-cpu:1 |
| whisper-base | openai-whisper-base-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | openai-whisper-base-generic-cpu:3 |
| whisper-tiny | openai-whisper-tiny-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | openai-whisper-tiny-generic-cpu:4 |
| olmo-3-7b-instruct | olmo-3-7b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | olmo-3-7b-instruct-generic-cpu:1 |
| smollm3-3b | smollm3-3b-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | smollm3-3b-generic-cpu:1 |
| mistral-nemo-12b-instruct | mistral-nemo-12b-instruct-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | mistral-nemo-12b-instruct-generic-cpu:1 |
| qwen3.5-2b-text | qwen3.5-2b-text-generic-cpu | Microsoft | chat-completion | ONNX | CPU | CPUExecutionProvider | qwen3.5-2b-text-generic-cpu:1 |
| whisper-large-v3-turbo | openai-whisper-large-v3-turbo-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | openai-whisper-large-v3-turbo-generic-cpu:4 |
| whisper-medium | openai-whisper-medium-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | openai-whisper-medium-generic-cpu:4 |
| whisper-small | openai-whisper-small-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | openai-whisper-small-generic-cpu:4 |
| nemotron-3.5-asr-streaming-0.6b | nemotron-3.5-asr-streaming-0.6b-generic-cpu | Microsoft | automatic-speech-recognition | ONNX | CPU | CPUExecutionProvider | nemotron-3.5-asr-streaming-0.6b-generic-cpu:3 |
| gpt-oss-20b | gpt-oss-20b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | gpt-oss-20b-cuda-gpu:1 |
| phi-4-mini-reasoning | Phi-4-mini-reasoning-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-4-mini-reasoning-cuda-gpu:3 |
| qwen2.5-0.5b | qwen2.5-0.5b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-0.5b-instruct-cuda-gpu:4 |
| qwen2.5-1.5b | qwen2.5-1.5b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-1.5b-instruct-cuda-gpu:4 |
| qwen2.5-coder-0.5b | qwen2.5-coder-0.5b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-coder-0.5b-instruct-cuda-gpu:4 |
| qwen2.5-coder-1.5b | qwen2.5-coder-1.5b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-coder-1.5b-instruct-cuda-gpu:4 |
| phi-4-mini | Phi-4-mini-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-4-mini-instruct-cuda-gpu:5 |
| qwen2.5-coder-14b | qwen2.5-coder-14b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-coder-14b-instruct-cuda-gpu:4 |
| qwen2.5-14b | qwen2.5-14b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-14b-instruct-cuda-gpu:4 |
| qwen2.5-coder-7b | qwen2.5-coder-7b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-coder-7b-instruct-cuda-gpu:4 |
| qwen2.5-7b | qwen2.5-7b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen2.5-7b-instruct-cuda-gpu:4 |
| phi-3-mini-128k | Phi-3-mini-128k-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-3-mini-128k-instruct-cuda-gpu:2 |
| phi-3.5-mini | Phi-3.5-mini-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-3.5-mini-instruct-cuda-gpu:2 |
| deepseek-r1-14b | deepseek-r1-distill-qwen-14b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | deepseek-r1-distill-qwen-14b-cuda-gpu:4 |
| phi-3-mini-4k | Phi-3-mini-4k-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-3-mini-4k-instruct-cuda-gpu:2 |
| phi-4 | Phi-4-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | Phi-4-cuda-gpu:2 |
| deepseek-r1-7b | deepseek-r1-distill-qwen-7b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | deepseek-r1-distill-qwen-7b-cuda-gpu:4 |
| mistral-7b-v0.2 | mistralai-Mistral-7B-Instruct-v0-2-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | mistralai-Mistral-7B-Instruct-v0-2-cuda-gpu:2 |
| qwen3-1.7b | qwen3-1.7b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3-1.7b-cuda-gpu:2 |
| qwen3-14b | qwen3-14b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3-14b-cuda-gpu:2 |
| qwen3-0.6b | qwen3-0.6b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3-0.6b-cuda-gpu:2 |
| qwen3-4b | qwen3-4b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3-4b-cuda-gpu:2 |
| qwen3-8b | qwen3-8b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3-8b-cuda-gpu:2 |
| olmo-3-7b-instruct | olmo-3-7b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | olmo-3-7b-instruct-cuda-gpu:1 |
| smollm3-3b | smollm3-3b-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | smollm3-3b-cuda-gpu:1 |
| mistral-nemo-12b-instruct | mistral-nemo-12b-instruct-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | mistral-nemo-12b-instruct-cuda-gpu:1 |
| qwen3.5-2b-text | qwen3.5-2b-text-cuda-gpu | Microsoft | chat-completion | ONNX | GPU | CUDAExecutionProvider | qwen3.5-2b-text-cuda-gpu:1 |
| whisper-base | openai-whisper-base-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | openai-whisper-base-cuda-gpu:3 |
| whisper-large-v3-turbo | openai-whisper-large-v3-turbo-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | openai-whisper-large-v3-turbo-cuda-gpu:3 |
| whisper-medium | openai-whisper-medium-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | openai-whisper-medium-cuda-gpu:3 |
| whisper-small | openai-whisper-small-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | openai-whisper-small-cuda-gpu:3 |
| whisper-tiny | openai-whisper-tiny-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | openai-whisper-tiny-cuda-gpu:3 |
| nemotron-3.5-asr-streaming-0.6b | nemotron-3.5-asr-streaming-0.6b-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | nemotron-3.5-asr-streaming-0.6b-cuda-gpu:2 |
| nemotron-speech-streaming-en-0.6b | nemotron-speech-streaming-en-0.6b-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | nemotron-speech-streaming-en-0.6b-cuda-gpu:1 |
| nemotron-speech-streaming-es-0.6b | nemotron-speech-streaming-es-0.6b-ft-cuda-gpu | Microsoft | automatic-speech-recognition | ONNX | GPU | CUDAExecutionProvider | nemotron-speech-streaming-es-0.6b-ft-cuda-gpu:1 |
| deepseek-r1-distill-qwen-1.5b | deepseek-ai-DeepSeek-R1-Distill-Qwen-1.5B | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-R1-Distill-Qwen-1.5B:1 |
| deepseek-r1-distill-qwen-7b | deepseek-ai-DeepSeek-R1-Distill-Qwen-7B | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-R1-Distill-Qwen-7B:4 |
| whisper-tiny | openai-whisper-tiny | — | automatic-speech-recognition | vllm | — | — | openai-whisper-tiny:1 |
| whisper-base | openai-whisper-base | — | automatic-speech-recognition | vllm | — | — | openai-whisper-base:1 |
| whisper-small | openai-whisper-small | — | automatic-speech-recognition | vllm | — | — | openai-whisper-small:1 |
| whisper-large-v3-turbo | openai-whisper-large-v3-turbo | — | automatic-speech-recognition | vllm | — | — | openai-whisper-large-v3-turbo:1 |
| ministral-3-3b-instruct-2512 | mistralai-Ministral-3-3B-Instruct-2512 | — | chat-completion | vllm | — | — | mistralai-Ministral-3-3B-Instruct-2512:1 |
| qwen3-0.6b | Qwen-Qwen3-0.6B | — | chat-completion | vllm | — | — | Qwen-Qwen3-0.6B:1 |
| qwen2.5-0.5b-instruct | Qwen-Qwen2.5-0.5B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-0.5B-Instruct:1 |
| qwen2.5-coder-0.5b-instruct | Qwen-Qwen2.5-Coder-0.5B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-Coder-0.5B-Instruct:1 |
| qwen2.5-1.5b-instruct | Qwen-Qwen2.5-1.5B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-1.5B-Instruct:1 |
| nemotron-speech-streaming-en-0.6b | nvidia-nemotron-speech-streaming-en-0.6b | — | automatic-speech-recognition | vllm | — | — | nvidia-nemotron-speech-streaming-en-0.6b:1 |
| qwen3-14b | Qwen-Qwen3-14B | — | chat-completion | vllm | — | — | Qwen-Qwen3-14B:1 |
| qwen3-1.7b | Qwen-Qwen3-1.7B | — | chat-completion | vllm | — | — | Qwen-Qwen3-1.7B:1 |
| qwen2.5-14b-instruct | Qwen-Qwen2.5-14B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-14B-Instruct:1 |
| nemotron-3-nano-30b-a3b-nvfp4 | nvidia-NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4:1 |
| smollm3-3b | HuggingFaceTB-SmolLM3-3B | — | chat-completion | vllm | — | — | HuggingFaceTB-SmolLM3-3B:1 |
| qwen3-8b | Qwen-Qwen3-8B | — | chat-completion | vllm | — | — | Qwen-Qwen3-8B:1 |
| openmath-nemotron-1.5b | nvidia-OpenMath-Nemotron-1.5B | — | chat-completion | vllm | — | — | nvidia-OpenMath-Nemotron-1.5B:1 |
| nemotron-nano-12b-v2 | nvidia-NVIDIA-Nemotron-Nano-12B-v2 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-12B-v2:1 |
| olmo-3-7b-instruct | allenai-Olmo-3-7B-Instruct | — | chat-completion | vllm | — | — | allenai-Olmo-3-7B-Instruct:1 |
| qwen3.5-4b | Qwen-Qwen3.5-4B | — | chat-completion | vllm | — | — | Qwen-Qwen3.5-4B:1 |
| nemotron-nano-9b-v2 | nvidia-NVIDIA-Nemotron-Nano-9B-v2 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-9B-v2:1 |
| nemotron-nano-12b-v2-vl-bf16 | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-BF16 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-BF16:1 |
| qwen2.5-coder-7b-instruct | Qwen-Qwen2.5-Coder-7B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-Coder-7B-Instruct:1 |
| qwen2.5-coder-1.5b-instruct | Qwen-Qwen2.5-Coder-1.5B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-Coder-1.5B-Instruct:1 |
| openreasoning-nemotron-1.5b | nvidia-OpenReasoning-Nemotron-1.5B | — | chat-completion | vllm | — | — | nvidia-OpenReasoning-Nemotron-1.5B:1 |
| qwen2.5-7b-instruct | Qwen-Qwen2.5-7B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-7B-Instruct:1 |
| nemotron-3-nano-4b-fp8 | nvidia-NVIDIA-Nemotron-3-Nano-4B-FP8 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Nano-4B-FP8:1 |
| qwen2.5-coder-14b-instruct | Qwen-Qwen2.5-Coder-14B-Instruct | — | chat-completion | vllm | — | — | Qwen-Qwen2.5-Coder-14B-Instruct:1 |
| acereason-nemotron-7b | nvidia-AceReason-Nemotron-7B | — | chat-completion | vllm | — | — | nvidia-AceReason-Nemotron-7B:1 |
| nemotron-nano-9b-v2-nvfp4 | nvidia-NVIDIA-Nemotron-Nano-9B-v2-NVFP4 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-9B-v2-NVFP4:1 |
| acereason-nemotron-1.1-7b | nvidia-AceReason-Nemotron-1.1-7B | — | chat-completion | vllm | — | — | nvidia-AceReason-Nemotron-1.1-7B:1 |
| nemotron-terminal-14b | nvidia-Nemotron-Terminal-14B | — | chat-completion | vllm | — | — | nvidia-Nemotron-Terminal-14B:1 |
| nemotron-terminal-8b | nvidia-Nemotron-Terminal-8B | — | chat-completion | vllm | — | — | nvidia-Nemotron-Terminal-8B:1 |
| nemotron-nano-12b-v2-vl-nvfp4-qad | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-NVFP4-QAD | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-NVFP4-QAD:1 |
| acemath-rl-nemotron-7b | nvidia-AceMath-RL-Nemotron-7B | — | chat-completion | vllm | — | — | nvidia-AceMath-RL-Nemotron-7B:1 |
| nemotron-nano-12b-v2-vl-fp8 | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-FP8 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-12B-v2-VL-FP8:1 |
| nemotron-nano-9b-v2-japanese | nvidia-NVIDIA-Nemotron-Nano-9B-v2-Japanese | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-9B-v2-Japanese:1 |
| nemotron-nano-9b-v2-fp8 | nvidia-NVIDIA-Nemotron-Nano-9B-v2-FP8 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-Nano-9B-v2-FP8:1 |
| nemotron-3-nano-4b-bf16 | nvidia-NVIDIA-Nemotron-3-Nano-4B-BF16 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Nano-4B-BF16:1 |
| nemotron-3-super-120b-a12b-nvfp4 | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4:1 |
| nemotron-4-mini-hindi-4b-instruct | nvidia-Nemotron-4-Mini-Hindi-4B-Instruct | — | chat-completion | vllm | — | — | nvidia-Nemotron-4-Mini-Hindi-4B-Instruct:1 |
| opencodereasoning-nemotron-14b | nvidia-OpenCodeReasoning-Nemotron-14B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-14B:1 |
| opencodereasoning-nemotron-7b | nvidia-OpenCodeReasoning-Nemotron-7B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-7B:1 |
| opencodereasoning-nemotron-1.1-7b | nvidia-OpenCodeReasoning-Nemotron-1.1-7B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-1.1-7B:1 |
| nemotron-3-nano-omni-30b-a3b-reasoning-fp8 | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8 | — | chat-completion | vllm | — | — | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8:1 |
| opencodereasoning-nemotron-1.1-14b | nvidia-OpenCodeReasoning-Nemotron-1.1-14B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-1.1-14B:1 |
| nemotron-3-nano-omni-30b-a3b-reasoning-nvfp4 | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4 | — | chat-completion | vllm | — | — | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-NVFP4:1 |
| pixtral-12b-2409 | mistralai-Pixtral-12B-2409 | — | chat-completion | vllm | — | — | mistralai-Pixtral-12B-2409:1 |
| nemotron-mini-4b-instruct | nvidia-Nemotron-Mini-4B-Instruct | — | chat-completion | vllm | — | — | nvidia-Nemotron-Mini-4B-Instruct:4 |
| acereason-nemotron-14b | nvidia-AceReason-Nemotron-14B | — | chat-completion | vllm | — | — | nvidia-AceReason-Nemotron-14B:3 |
| whisper-medium | openai-whisper-medium | — | automatic-speech-recognition | vllm | — | — | openai-whisper-medium:2 |
| openmath-nemotron-14b-kaggle | nvidia-OpenMath-Nemotron-14B-Kaggle | — | chat-completion | vllm | — | — | nvidia-OpenMath-Nemotron-14B-Kaggle:3 |
| nemotron-3-nano-omni-30b-a3b-reasoning-bf16 | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 | — | chat-completion | vllm | — | — | nvidia-Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16:2 |
| olmo-3.1-32b-instruct | allenai-Olmo-3.1-32B-Instruct | — | chat-completion | vllm | — | — | allenai-Olmo-3.1-32B-Instruct:2 |
| nemotron-terminal-32b | nvidia-Nemotron-Terminal-32B | — | chat-completion | vllm | — | — | nvidia-Nemotron-Terminal-32B:2 |
| openmath-nemotron-32b | nvidia-OpenMath-Nemotron-32B | — | chat-completion | vllm | — | — | nvidia-OpenMath-Nemotron-32B:2 |
| opencodereasoning-nemotron-32b | nvidia-OpenCodeReasoning-Nemotron-32B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-32B:2 |
| deepseek-r1-distill-qwen-14b | deepseek-ai-DeepSeek-R1-Distill-Qwen-14B | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-R1-Distill-Qwen-14B:3 |
| openreasoning-nemotron-14b | nvidia-OpenReasoning-Nemotron-14B | — | chat-completion | vllm | — | — | nvidia-OpenReasoning-Nemotron-14B:3 |
| opencodereasoning-nemotron-1.1-32b | nvidia-OpenCodeReasoning-Nemotron-1.1-32B | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-1.1-32B:2 |
| mistral-small-4-119b-2603-nvfp4 | mistralai-Mistral-Small-4-119B-2603-NVFP4 | — | chat-completion | vllm | — | — | mistralai-Mistral-Small-4-119B-2603-NVFP4:2 |
| opencodereasoning-nemotron-32b-ioi | nvidia-OpenCodeReasoning-Nemotron-32B-IOI | — | chat-completion | vllm | — | — | nvidia-OpenCodeReasoning-Nemotron-32B-IOI:2 |
| qwen3-32b | Qwen-Qwen3-32B | — | chat-completion | vllm | — | — | Qwen-Qwen3-32B:2 |
| openreasoning-nemotron-32b | nvidia-OpenReasoning-Nemotron-32B | — | chat-completion | vllm | — | — | nvidia-OpenReasoning-Nemotron-32B:2 |
| openmath-nemotron-14b | nvidia-OpenMath-Nemotron-14B | — | chat-completion | vllm | — | — | nvidia-OpenMath-Nemotron-14B:3 |
| nemotron-3-super-120b-a12b-fp8 | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-FP8 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-FP8:2 |
| magistral-small-2509 | mistralai-Magistral-Small-2509 | — | chat-completion | vllm | — | — | mistralai-Magistral-Small-2509:4 |
| mathstral-7b-v0.1 | mistralai-Mathstral-7B-v0.1 | — | chat-completion | vllm | — | — | mistralai-Mathstral-7B-v0.1:2 |
| devstral-small-2505 | mistralai-Devstral-Small-2505 | — | chat-completion | vllm | — | — | mistralai-Devstral-Small-2505:4 |
| openreasoning-nemotron-7b | nvidia-OpenReasoning-Nemotron-7B | — | chat-completion | vllm | — | — | nvidia-OpenReasoning-Nemotron-7B:2 |
| mistral-nemo-instruct-fp8-2407 | mistralai-Mistral-Nemo-Instruct-FP8-2407 | — | chat-completion | vllm | — | — | mistralai-Mistral-Nemo-Instruct-FP8-2407:2 |
| openmath-nemotron-7b | nvidia-OpenMath-Nemotron-7B | — | chat-completion | vllm | — | — | nvidia-OpenMath-Nemotron-7B:2 |
| mistral-7b-instruct-v0.3 | mistralai-Mistral-7B-Instruct-v0.3 | — | chat-completion | vllm | — | — | mistralai-Mistral-7B-Instruct-v0.3:4 |
| mixtral-8x7b-instruct-v0.1 | mistralai-Mixtral-8x7B-Instruct-v0.1 | — | chat-completion | vllm | — | — | mistralai-Mixtral-8x7B-Instruct-v0.1:2 |
| ministral-3-8b-instruct-2512 | mistralai-Ministral-3-8B-Instruct-2512 | — | chat-completion | vllm | — | — | mistralai-Ministral-3-8B-Instruct-2512:2 |
| ministral-3-14b-instruct-2512 | mistralai-Ministral-3-14B-Instruct-2512 | — | chat-completion | vllm | — | — | mistralai-Ministral-3-14B-Instruct-2512:2 |
| nemotron-3-super-120b-a12b-bf16 | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Super-120B-A12B-BF16:2 |
| mixtral-8x22b-instruct-v0.1 | mistralai-Mixtral-8x22B-Instruct-v0.1 | — | chat-completion | vllm | — | — | mistralai-Mixtral-8x22B-Instruct-v0.1:2 |
| devstral-small-2507 | mistralai-Devstral-Small-2507 | — | chat-completion | vllm | — | — | mistralai-Devstral-Small-2507:4 |
| mistral-small-4-119b-2603 | mistralai-Mistral-Small-4-119B-2603 | — | chat-completion | vllm | — | — | mistralai-Mistral-Small-4-119B-2603:2 |
| magistral-small-2507 | mistralai-Magistral-Small-2507 | — | chat-completion | vllm | — | — | mistralai-Magistral-Small-2507:4 |
| magistral-small-2506 | mistralai-Magistral-Small-2506 | — | chat-completion | vllm | — | — | mistralai-Magistral-Small-2506:3 |
| deepseek-v3-0324 | deepseek-ai-DeepSeek-V3-0324 | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-V3-0324:4 |
| deepseek-v3.1 | deepseek-ai-DeepSeek-V3.1 | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-V3.1:4 |
| deepseek-v3.2 | deepseek-ai-DeepSeek-V3.2 | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-V3.2:4 |
| deepseek-v3.2-speciale | deepseek-ai-DeepSeek-V3.2-Speciale | — | chat-completion | vllm | — | — | deepseek-ai-DeepSeek-V3.2-Speciale:4 |
| mistral-large-3-675b-instruct-2512 | mistralai-Mistral-Large-3-675B-Instruct-2512 | — | chat-completion | vllm | — | — | mistralai-Mistral-Large-3-675B-Instruct-2512:5 |
| nemotron-3-nano-30b-a3b-bf16 | nvidia-NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | — | chat-completion | vllm | — | — | nvidia-NVIDIA-Nemotron-3-Nano-30B-A3B-BF16:4 |
| ministral-3-14b-reasoning-2512 | mistralai-Ministral-3-14B-Reasoning-2512 | — | chat-completion | vllm | — | — | mistralai-Ministral-3-14B-Reasoning-2512:3 |
| mistral-small-24b-instruct-2501 | mistralai-Mistral-Small-24B-Instruct-2501 | — | chat-completion | vllm | — | — | mistralai-Mistral-Small-24B-Instruct-2501:5 |
| mistral-nemo-instruct-2407 | mistralai-Mistral-Nemo-Instruct-2407 | — | chat-completion | vllm | — | — | mistralai-Mistral-Nemo-Instruct-2407:4 |
| phi-4-mini-instruct | microsoft-Phi-4-mini-instruct | — | chat-completion | vllm | — | — | microsoft-Phi-4-mini-instruct:1 |
| phi-3.5-mini-instruct | microsoft-Phi-3-5-mini-instruct | — | chat-completion | vllm | — | — | microsoft-Phi-3-5-mini-instruct:1 |
| phi-4-mini-reasoning | microsoft-Phi-4-mini-reasoning | — | chat-completion | vllm | — | — | microsoft-Phi-4-mini-reasoning:1 |
| phi-4 | microsoft-phi-4 | — | chat-completion | vllm | — | — | microsoft-phi-4:1 |
| phi-4-reasoning | microsoft-Phi-4-reasoning | — | chat-completion | vllm | — | — | microsoft-Phi-4-reasoning:1 |
| gpt-oss-20b | openai-gpt-oss-20b | — | chat-completion | vllm | — | — | openai-gpt-oss-20b:1 |
| mistral-7b-instruct-v0.2 | mistralai-Mistral-7B-Instruct-v0-2 | — | chat-completion | vllm | — | — | mistralai-Mistral-7B-Instruct-v0-2:2 |
| gpt-oss-120b | openai-gpt-oss-120b | — | chat-completion | vllm | — | — | openai-gpt-oss-120b:4 |
| mistral-small-3.2-24b-instruct-2506 | mistralai-mistral-small-3-2-24b-instruct-2506 | — | chat-completion | vllm | — | — | mistralai-mistral-small-3-2-24b-instruct-2506:8 |
| mistral-small-3.1-24b-instruct-2503 | mistralai-Mistral-Small-3-1-24B-Instruct-2503 | — | chat-completion | vllm | — | — | mistralai-Mistral-Small-3-1-24B-Instruct-2503:4 |
