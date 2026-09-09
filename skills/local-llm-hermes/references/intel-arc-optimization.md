# Intel Arc GPU Optimization for Local LLM Inference

Intel Arc GPUs (A-series: A310/A380/A580/A750/A770; Battlemage: B580/B570) use
the **SYCL/oneAPI** backend — not CUDA (NVIDIA) or ROCm (AMD).

## Backend performance (best to worst, 2026)

1. **SYCL (oneAPI 2026.1+, FP16 build)** — fastest, now beats Vulkan on Arc
2. **IPEX-LLM** — Intel's official stack, wraps llama.cpp/Ollama/LM Studio
3. **Vulkan** — simpler setup, no Intel SDK needed, 10-20% slower than SYCL
4. **CPU fallback** — only for models that don't fit VRAM

## IPEX-LLM (recommended path)

Intel's `ipex-llm` is the easiest way to get SYCL acceleration:

```bash
pip install ipex-llm
```

It auto-detects Arc GPUs and injects SYCL acceleration into:
- Ollama (`ipex-llm[cpp]`)
- llama.cpp
- LM Studio (via Bionic port)
- vLLM
- HuggingFace transformers

https://github.com/intel/ipex-llm

## LM Studio Bionic

Prebuilt LM Studio port optimized for Intel Arc. Same port (1234) and API
as regular LM Studio. Download from LM Studio website — select the Bionic/Arc build.

## llama.cpp with SYCL (manual build)

```bash
# Requires Intel oneAPI Base Toolkit
# https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
mkdir build && cd build

# Windows (oneAPI environment)
cmake .. -G "Ninja" -DGGML_SYCL=ON -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx
cmake --build . --config Release

# Verify
./bin/llama-cli --list-devices
```

Key env vars:
```
ONEAPI_DEVICE_SELECTOR=level_zero:gpu
GGML_SYCL_DEVICE=0
```

## VRAM requirements (Intel Arc)

| Model | Quant | VRAM |
|-------|-------|------|
| Qwen 3 8B | Q4_K_M | ~5 GB |
| Qwen 3 14B | Q4_K_M | ~9 GB |
| Llama 3.1 8B | Q4_K_M | ~5 GB |
| DeepSeek R1 Distill 7B | Q4_K_M | ~4.5 GB |
| Phi-4 14B | Q4_K_M | ~9 GB |

Arc A770 (16GB): fits most 8B+ models at Q5/Q6.
Arc A750 (8GB): fits 8B at Q4, 14B borderline.
Arc A380 (6GB): 3B-8B at Q4, consider IQ quants.

## Driver requirements

- Intel Arc GPU drivers: latest WHQL
- oneAPI Base Toolkit 2026.1+ (for SYCL builds)
- GPU firmware: check `intel-gpu-tools` / Intel Graphics Command Center