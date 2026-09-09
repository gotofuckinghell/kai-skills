---
name: local-llm-hermes
description: Run Hermes on local LLMs. Switch cloud/local mid-session.
version: 1.1.0
author: Hermes Agent
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [local-llm, ollama, lm-studio, llama-cpp, model-switching, custom-provider, aliases, auto-detect]
---

# Local LLM with Hermes Agent

Run Hermes entirely on a local model — no cloud, no API keys, full privacy. Set up one `custom` provider pointed at your local inference server, create a model alias, and switch between cloud and local with `/model <name>`.

## When to use

- User wants to run Hermes on a local LLM (Ollama, LM Studio, llama.cpp, LM Studio Bionic, vLLM, KoboldCPP, etc.)
- User wants fast switching between cloud provider (OpenRouter, Anthropic, ...) and local model
- User asks "how to use local model with Hermes", "switch between local and cloud", or "connect LM Studio to Hermes"
- User needs to debug local model connectivity (wrong port, wrong model name, tool calling not working)

## Quick setup

### 1. Start your local server

Make sure the local inference server is running with an OpenAI-compatible endpoint:

| Server | Default base_url | Notes |
|--------|-----------------|-------|
| LM Studio | `http://localhost:1234/v1` | GUI, good model discovery |
| LM Studio Bionic | `http://localhost:1234/v1` | Intel Arc-optimized port |
| Ollama | `http://localhost:11434/v1` | Lightweight, GGUF-only |
| llama.cpp server | `http://localhost:8080/v1` | Full control |
| vLLM | `http://localhost:8000/v1` | Server-grade, needs CUDA/ROCm |
| KoboldCPP | `http://localhost:5001/v1` | Lightweight, vintage formats |
| Lemonade | `http://localhost:13305/v1` | AMD NPU + GPU (mobile Ryzen AI only) |

### 2. Create a model alias

**Full form with `model_aliases` (top-level key)** — required for full provider override (custom base_url, custom api_key):

```bash
hermes config set model_aliases.local.provider custom
hermes config set model_aliases.local.model "model-name-as-server-sees-it"
hermes config set model_aliases.local.base_url "http://localhost:PORT/v1"
hermes config set model_aliases.local.api_key "dummy"
hermes config set model_aliases.local.context_length 131072
```

**Shortcut form (`model.aliases`)** — works when only the model name changes within the same provider:

```bash
hermes config set model.aliases.local "custom/qwen3:14b"
```

For full provider override, you need `model_aliases` (top-level key), not `model.aliases` (nested under `model`).
Only `model_aliases` supports full `provider`, `base_url`, `api_key`, and `context_length` overrides.

### 3. Auto-detect loaded model in LM Studio (optional)

LM Studio loads one model at a time, but `/v1/models` returns ALL downloaded models. Hardcoding a model name
in the alias breaks when you switch models in LM Studio. Use the auto-detect proxy instead:

1. Copy `scripts/lmstudio-proxy.py` to `~/.hermes/scripts/`
2. Start it: `python ~/.hermes/scripts/lmstudio-proxy.py` (listens on `127.0.0.1:1235`)
3. Configure the alias with `model: __auto__`:

```bash
hermes config set model_aliases.local.model "__auto__"
hermes config set model_aliases.local.provider custom
hermes config set model_aliases.local.base_url "http://localhost:1235/v1"
hermes config set model_aliases.local.api_key lm-studio
hermes config set model_aliases.local.context_length 131072
```

Now `/model local` detects whichever model is loaded in LM Studio — no manual config updates needed.

The proxy probes all models in parallel: the loaded one responds in <1s; the proxy substitutes its name
and forwards the request. Cache TTL is 30 seconds. See `references/lmstudio-auto-detect-proxy.md` for details.

### 4. Switch models

```bash
/model local       # → local model
/model deepseek    # → OpenRouter DeepSeek (built-in alias)
/model sonnet      # → Anthropic Claude (built-in alias)
```

Built-in aliases: `sonnet`, `opus`, `haiku`, `claude`, `gpt5`, `gpt`, `codex`, `o3`, `o4`, `gemini`, `deepseek`, `grok`, `llama`, `qwen`, `minimax`, `nemotron`, `kimi`, `glm`, `step`, `mimo`, `trinity`.

## Update model name after switching local models

```bash
hermes config set model.aliases.local.model "new-model-name"
```

Find the model name in your server's UI (LM Studio shows it as "Loaded model: ..."; Lemonade: `lemonade list`, Ollama: `ollama list`).

## Tool calling requirement

The local model **must** support tool/function calling. Good choices:

- Qwen 2.5 / Qwen 3 (all sizes) — strong tool calling
- Llama 3.1+ (8B and up) — reliable
- DeepSeek R1 distillations — works but slower
- Mistral Nemo / Small — moderate support
- Phi-4 — hit or miss on tool calling

Smaller models (<3B) often fail to produce valid tool calls. If `/model local` produces broken output or hangs, the model likely doesn't support tool calling.

## Hardware-specific notes

### AMD Ryzen 9000 desktop (9950X, 9950X3D, etc.)
- **No NPU** — XDNA NPU is only in mobile Ryzen AI (Strix Point, Hawk Point, Phoenix)
- Has iGPU (basic RDNA 2, 2 CUs) — enough for Vulkan llama.cpp but not fast
- CPU-only inference benefits from AVX-512
- For AMD GPU: ROCm on Linux, Vulkan on Windows

### Intel Arc GPU
- Use **SYCL/oneAPI** backend (not CUDA, not ROCm)
- **IPEX-LLM** (`intel/ipex-llm`) wraps llama.cpp with oneAPI acceleration
- LM Studio Bionic is pre-optimized for Intel Arc
- SYCL now outperforms Vulkan on Arc with oneAPI 2026.1 + fresh drivers
- Vulkan is the simpler fallback

### AMD NPU (mobile — NOT desktop)
- Lemonade + `flm` or `ryzenai-llm` recipe
- Splits work: NPU for prompt processing, iGPU for token generation
- If the user says "Lemonade" but has a desktop chip, warn them NPU won't work

## Switching back to cloud provider

```bash
/model deepseek     # built-in alias → your default OpenRouter model
# or
/model sonnet       # → Anthropic Claude
```

No config needed — built-in aliases always resolve through your configured primary provider.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `/model local` hangs | Wrong port or model name | Check server is running; verify model name |
| First message returns empty/broken | Model lacks tool calling | Try a larger/capable model (Qwen 3 8B+) |
| "Connection refused" | Server not started | Start LM Studio / Ollama first |
| Model loads but outputs garbage | Chat template mismatch | Most servers auto-detect; check server logs |
| SYCL backend slower than Vulkan | Old oneAPI / drivers | Update to oneAPI 2026.1+, latest Intel GPU drivers |

## See also

- `references/intel-arc-optimization.md` — SYCL, IPEX-LLM, driver guide for Intel Arc
- Hermes docs: https://hermes-agent.nousresearch.com/docs/
- Provider config reference: `hermes-agent` skill → `references/providers-and-models.md`