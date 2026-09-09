---
name: local-llm-inference
description: "Connect local LLM servers to Hermes via custom provider."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [local-llm, ollama, lm-studio, llama.cpp, lemonade, koboldcpp, vllm, npu, amd, gguf, custom-provider]
    related_skills: [llama-cpp, hermes-agent]
---

# Local LLM Inference

Set up any local LLM inference backend and wire it to Hermes Agent as a custom provider. Covers Ollama, LM Studio, llama.cpp, Lemonade (AMD NPU), KoboldCPP, vLLM, and any other OpenAI-compatible server.

## When to use

- User wants to run Hermes on a local model instead of a cloud API
- User asks how to connect Ollama / LM Studio / llama.cpp to Hermes
- User has AMD hardware and wants NPU-accelerated inference
- User wants to download uncensored/unrestricted models from HuggingFace
- User asks about local model options for their specific hardware

## General pattern: wiring any local server to Hermes

Every local backend exposes an OpenAI-compatible `/v1` endpoint. Connect it with:

```bash
hermes config set model.provider custom
hermes config set model.default "<model-name-as-seen-by-backend>"
hermes config set model.base_url "http://localhost:<PORT>/v1"
hermes config set model.api_key <any-non-empty-string>
```

`api_key` must be set (Hermes requires it) but local servers don't validate it — use `ollama`, `lm-studio`, `not-needed`, or any placeholder.

## Backend reference

| Backend | Default base_url | Port | Windows? | Notes |
|---------|-----------------|------|----------|-------|
| **Ollama** | `http://localhost:11434/v1` | 11434 | Yes | Easiest; `ollama pull <model>` then ready |
| **LM Studio** | `http://localhost:1234/v1` | 1234 | Yes | GUI, built-in HF model browser, Vulkan/CUDA |
| **llama.cpp** (server) | `http://localhost:8080/v1` | 8080 | Yes | Max control; `llama-server -hf repo:quant` |
| **Lemonade** (AMD) | `http://localhost:13305/v1` | 13305 | Yes | NPU+iGPU hybrid; AMD's native local server |
| **KoboldCPP** | `http://localhost:5001/v1` | 5001 | Yes | Lightweight, legacy formats, GGUF |
| **vLLM** | `http://localhost:8000/v1` | 8000 | Linux | High-throughput, PagedAttention, batched |
| **text-generation-webui** | `http://localhost:5000/v1` | 5000 | Yes | Multi-format, LoRA, extension ecosystem |
| **LocalAI** | `http://localhost:8080/v1` | 8080 | Docker | Multi-backend, containerized |

## AMD NPU: Lemonade

AMD XDNA NPU does NOT work with vLLM (architecture mismatch — NPU requires ONNX/Vitis AI, not raw PyTorch weights). AMD's own solution is **Lemonade** — a local LLM server that splits work across NPU (first-token latency) and iGPU (token generation).

### Adding custom models

**Pull from HuggingFace (recommended):**
```bash
lemonade pull unsloth/Qwen3-8B-GGUF         # interactive quant picker
lemonade pull unsloth/Qwen3-8B-GGUF:Q4_K_M  # specific quant
lemonade pull https://huggingface.co/bartowski/CultriX-8B-GGUF:Q4_K_M
```

**Use a local GGUF file (no download):**
Drop `.gguf` files into `%USERPROFILE%\.config\lemonade\extra-models\` — they appear as `extra.<filename>` immediately. No config editing needed.

**Full custom registration:**
```bash
lemonade pull user.MyModel \
    --checkpoint main org/repo:Q4_K_M \
    --recipe llamacpp \
    --label chat \
    --label tool-calling
```

### Connecting Lemonade to Hermes
```bash
hermes config set model.provider custom
hermes config set model.default "user.MyModel"
hermes config set model.base_url "http://localhost:13305/v1"
hermes config set model.api_key lemonade
```

See `references/lemonade-custom-models.md` for full documentation on checkpoints, multi-file models, recipe options, and collections.

## Model alias pattern (coexist with cloud)

To switch between cloud and local WITHOUT changing your global default, use a top-level `model_aliases` entry (full provider override including `base_url`):

```bash
hermes config set model_aliases.local.provider custom
hermes config set model_aliases.local.model "model-name-as-server-sees-it"
hermes config set model_aliases.local.base_url "http://localhost:PORT/v1"
hermes config set model_aliases.local.api_key "placeholder"
hermes config set model_aliases.local.context_length 131072
# Then in-session: /model local   (switches to local)
# /model deepseek                  (back to cloud)
```

Use `model_aliases` (top-level YAML key), NOT `model.aliases` (nested under `model`). The nested form can only change the model name within the same provider — it cannot set a custom `base_url`, which every local server needs. See `local-llm-hermes` skill for the full workflow with auto-detection.

## Uncensored / unrestricted model sources

See `references/uncensored-models.md` for a curated list of HuggingFace repos with GGUF quants of uncensored models.

## Pitfalls

- **Ollama models and tool calling**: many Ollama-tagged models lack function-calling support. Prefer Qwen 2.5/3 or Llama 3.1+ for tool calling. Test with a simple tool-using prompt before committing.
- **AMD NPU on Windows**: ROCm is not officially supported on Windows. Lemonade is the only first-party path. LM Studio on Windows uses Vulkan (iGPU), not NPU.
- **Context size**: local servers often default to small context windows (2048). Override with `--ctx-size` or the server's config. For Hermes agent use, 8192+ is recommended.
- **Model format**: GGUF is the universal format — works across Ollama, LM Studio, llama.cpp, KoboldCPP, and Lemonade. When downloading from HF, always prefer GGUF repos.
- **Tool-calling quality gap**: local models are worse at following complex tool-calling instructions than cloud models (DeepSeek V4, Claude). For simple tasks they work; for multi-step autonomous agent workflows, expect more errors.