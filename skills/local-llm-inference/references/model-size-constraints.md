# Model Size Constraints

## The 27B Reality

27B-parameter models (Gemma 3 27B, Qwen 3.8 27B, Llama 3 27B) are too large for consumer GPUs:

- Q3_K_M quant: ~53 GB
- Q4_K_M quant: ~58 GB
- Largest consumer GPU: RTX 4090 = 24 GB, Arc A770 = 16 GB

These models **cannot** fit entirely in VRAM. Partial GPU offload (llama.cpp `-ngl N`) results in CPU-bound inference — prompt processing runs at ~13 ms/token instead of ~0.5 ms/token on pure GPU.

**Result for Hermes Agent users:** 4-5 tokens/sec, 30-60 seconds per prompt (Hermes system prompt = 20-30K tokens), 1-5 minutes per response. Unusable.

## Safe Sizes

For consumer hardware running Hermes Agent locally, use **≤14B models**:

| Model | Size (Q4) | Tool calling | Fits on |
|-------|----------|-------------|---------|
| Qwen 3 9B | ~6 GB | Excellent | Any GPU with 6+ GB |
| Llama 3.1 8B | ~5 GB | Good | Any GPU with 4+ GB |
| Qwen 2.5 14B | ~9 GB | Excellent | Arc A770, RTX 3060+ |
| Qwen 3.8 9B | ~6 GB | Good | Any GPU with 6+ GB |