# DirectML Provider Reference

## Verified Working Stack (Intel Arc A770 4GB + AMD Radeon 2GB, Vulkan 1.4.350)

| Component | Version | Role |
|-----------|---------|------|
| `onnxruntime-directml` | 1.24.4 | ONNX runtime with DirectML EP |
| `rapidocr_onnxruntime` | 1.4.4 | OCR detection + recognition |
| `pymupdf` | 1.28.2 | PDF rendering to images |

**DO NOT install**: plain `onnxruntime` (CPU/Azure only, no DirectML).

## Provider Order

```python
providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
```

DML first, CPU fallback.

## Benchmark (Intel Arc A770 4GB)

| Input | Time |
|-------|------|
| 4576x3432 JPG | ~1.54 sec |
| 1772x1263 PNG | ~2.90 sec |
| easyocr CPU | ~6.7 sec |

## Alternatives That Do NOT Work on Non-NVIDIA Hardware

- `easyocr` + `torch-directml` — CUDA runtime error
- `paddlepaddle-gpu` — CUDA-only, silent fallback
- `pytesseract` — no Tesseract binary
- `pymupdf` + DJVU — no DJVU handler
- plain `onnxruntime` — CPU/Azure only

## GPU Hardware

- Intel Arc A770 4 GB (DirectX 12)
- AMD Radeon Graphics 2 GB (Integrated)
- Vulkan 1.4.350

No NVIDIA GPU present.
