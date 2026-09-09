# Model Size & Alias Pitfalls (session-learned)

## 27B models do NOT fit consumer hardware

Gemma 3 27B / Qwen3.8 27B in Q3_K_M need ~53 GB total memory (RAM + VRAM combined). No consumer GPU has enough VRAM (Arc A770 = 16 GB, RTX 3060 = 12 GB), so the model spills to CPU and runs at 4-5 tok/s with 30-60s prompt eval. LM Studio / llama.cpp will refuse or crawl.

**Rule: recommend ≤9B models for consumer GPUs.** Qwen 3 9B (~6 GB in Q4), Llama 3.1 8B (~5 GB), Mistral Nemo 12B (borderline). 27B is only viable with 48+ GB unified memory (Mac Studio M2 Ultra, mobile with huge unified RAM) or a data-center GPU.

### How to diagnose from LM Studio logs

The log line `n_gpu_layers already set by user to N` plus `layer 0 is assigned to device CPU but fused ... assigned to device Vulkan0` means partial offload — some layers on GPU, rest on CPU. This is the slow path. Prompt eval ~12-15 ms/token and generation ~4-5 tok/s confirm CPU-bound operation.

## Alias forms: model_aliases vs model.aliases

Two DIFFERENT config keys, easy to confuse:

- `model_aliases.<name>.*` (TOP-LEVEL key) — full override. Supports `provider`, `model`, `base_url`, `api_key`, `context_length`. REQUIRED for local servers because they need a custom base_url.
- `model.aliases.<name>` (nested under `model`) — shortcut only. Just maps a name to a model string within the current provider. CANNOT set base_url or api_key.

**Symptom of using the wrong one:** `/model local` fails with `✗ Model 'local' was not found in this provider's model listing.` — because Hermes is trying to find "local" as a model name inside OpenRouter instead of resolving a custom endpoint.

**Fix:** use `hermes config set model_aliases.local.provider custom` (top-level `model_aliases`, not `model.aliases`).

## Context length override

Hermes hard-requires 64K context. Local servers often report half the true context (LM Studio reported 32,256 for Gemma 3 27B which actually has 128K). Set `context_length` in the alias to the model's true max:

```bash
hermes config set model_aliases.local.context_length 131072
```

Symptom without it: `Failed to initialize agent: Model ... has a context window of 32,256 tokens, which is below the minimum 64,000 required.`
