# Uncensored / Unrestricted GGUF Models on HuggingFace

Curated repos with GGUF quants of models without alignment restrictions. All are pull-ready for Ollama, LM Studio, llama.cpp, KoboldCPP, and Lemonade.

## Chat / General purpose

| Repo | Base model | Size (Q4) | Notes |
|------|-----------|-----------|-------|
| `bartowski/CultriX-8B-GGUF` | Llama-3.1 8B | ~5 GB | General uncensored |
| `mradermacher/EVA-Qwen3-14B-GGUF` | Qwen3 14B | ~9 GB | Strong reasoning, uncensored |
| `mradermacher/DarkIdol-Llama-3.1-8B-Instruct-1.2B-GGUF` | Llama-3.1 1B | ~800 MB | Tiny, fast |

## Roleplay / creative

| Repo | Base model | Size (Q4) | Notes |
|------|-----------|-----------|-------|
| `mradermacher/MN-12B-Lyra-v4-GGUF` | Magnum 12B | ~7 GB | Roleplay-focused |
| `bartowski/NemoMix-Unleashed-12B-GGUF` | Mistral Nemo 12B | ~7 GB | Creative writing |

## Coding

| Repo | Base model | Size (Q4) | Notes |
|------|-----------|-----------|-------|
| `bartowski/Qwen3-Coder-30B-A3B-GGUF` | Qwen3 MoE 30B | ~18 GB | Strong code, MoE |
| `mradermacher/DeepSeek-Coder-V2-Lite-Instruct-GGUF` | DeepSeek Coder V2 | ~9 GB | Code specialist |

## Abliterated (surgical uncensoring)

"Abliteration" removes refusal directions from model weights without retraining.

| Repo | Base | Size (Q4) |
|------|------|-----------|
| `failspy/Llama-3.1-8B-Instruct-abliterated-GGUF` | Llama-3.1 8B | ~5 GB |
| `failspy/Meta-Llama-3.1-70B-Instruct-abliterated-GGUF` | Llama-3.1 70B | ~40 GB |
| `huihui-ai/Qwen3-14B-abliterated-GGUF` | Qwen3 14B | ~9 GB |
| `huihui-ai/Qwen3-32B-abliterated-GGUF` | Qwen3 32B | ~20 GB |

## How to pull

```bash
# Ollama: create a Modelfile with FROM pointing to HF GGUF URL
# LM Studio: search by repo name in the built-in browser
# llama.cpp: llama-server -hf bartowski/CultriX-8B-GGUF:Q4_K_M
# Lemonade: lemonade pull bartowski/CultriX-8B-GGUF:Q4_K_M
# KoboldCPP: download the .gguf manually, load via GUI
```

## Quant recommendation for uncensored models

- **Q4_K_M** — best balance for 8B–14B models (most popular)
- **Q5_K_M** — better quality, marginal size increase (~15%)
- **Q3_K_M** — for tight RAM/VRAM budgets
- **Q8_0** — near-lossless, only if you have the memory

## Finding more

Search HuggingFace: https://huggingface.co/models?search=abliterated+GGUF&sort=trending

Key uploaders with consistent quality: `bartowski`, `mradermacher`, `failspy`, `huihui-ai`, `unsloth`.