# Model Size Reality Check

## 27B models and consumer hardware

27B-parameter models (Gemma 3 27B, Qwen 3.8 27B, Llama 3 27B) are too large for consumer GPUs:

| Quantization | Approx size | Can consumer GPU fit it? |
|-------------|------------|--------------------------|
| Q3_K_M | ~53 GB | No — even RTX 4090 (24 GB) can't |
| Q4_K_M | ~58 GB | No |
| Q5_K_M | ~65 GB | No |
| Q8 | ~80 GB | No |
| F16 | ~150 GB | No |

Even with partial GPU offload (llama.cpp `-ngl`), prompt processing becomes **CPU-bound** (~13 ms/token instead of ~0.5 ms/token on GPU), making Hermes Agent **unusable** (4-5 tokens/sec, 1-5 minutes per response due to Hermes's large system prompt of 20-30K tokens).

## What actually fits

| Model size | Q4 approx size | Fits on |
|-----------|---------------|---------|
| 1-3B | 1-2 GB | Any GPU |
| 7-8B | 4-6 GB | GTX 1060+, Arc A380+, RX 580+ |
| 9-12B | 6-8 GB | RTX 2060+, Arc A750+, RX 6600+ |
| 14B | 9-10 GB | RTX 3060+, Arc A770, RX 6700+ |
| 27B+ | 50+ GB | Only multi-GPU server or Mac Studio (128 GB unified) |

## Recommended models for Hermes on consumer hardware

- **Qwen 3 8-14B** (Q4_K_M) — best tool calling, ~5-9 GB
- **Llama 3.1 8B** (Q4_K_M) — reliable, ~5 GB
- **Qwen 2.5 14B** (Q4_K_M) — strong reasoning, ~9 GB
- **DeepSeek R1 distill 14B** (Q4_K_M) — chain-of-thought, ~9 GB

## LM Studio log diagnosis

When slow (5+ min responses), check `%USERPROFILE%\.lmstudio\server-logs\`:

```
# Fast (all GPU):
n_gpu_layers = 42, no "layer X is assigned to device CPU"

# Slow (CPU-bound):
n_gpu_layers already set by user to N (N < total layers)
layer 0 is assigned to device CPU but fused ... is assigned to device Vulkan0
fused ... not supported, set to disabled
```

Key metric: `prompt eval time = X ms / N tokens (Y ms per token)`
- <1 ms/token = GPU-bound (good)
- 10+ ms/token = CPU-bound (slow, model too big)