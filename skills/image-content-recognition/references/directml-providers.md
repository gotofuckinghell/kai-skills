# DirectML Provider Reference

## Verified Working Stack (Intel Arc A770 4GB + AMD Radeon 2GB, Vulkan 1.4.350)

| Component | Version | Role |
|-----------|---------|------|
| `onnxruntime-directml` | 1.24.4 | ONNX runtime with DirectML EP |
| `rapidocr_onnxruntime` | 1.4.4 | OCR detection + recognition |
| `pymupdf` | 1.28.2 | PDF rendering to images |
| `onnxruntime` (for vision) | via `onnxruntime-directml` | DirectML-enabled ONNX runtime |

**DO NOT install**: plain `onnxruntime` (CPU/Azure only, no DirectML).

## Provider Order

```python
providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
```

DML first, CPU fallback.

## Benchmark

| Task | Input | Time |
|------|-------|------|
| OCR | 4576x3432 JPG | ~1.54 sec |
| OCR | 1772x1263 PNG | ~2.90 sec |
| OCR | easyocr CPU | ~6.7 sec |
| ImageNet classify | mobilenetv2 | ~10-500ms |

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
- No NVIDIA GPU present

## ONNX Vision Models

### ImageNet Classification (MobileNetV2)
- Model: `mobilenetv2-10.onnx` (~14MB)
- Input: 224x224 RGB, float32
- Output: 1000 class logits
- Preprocessing: ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Pitfall: Must cast to `np.float32` explicitly. `np.array(img)` may produce float64 causing ONNX InvalidArgument error.

### Florence-2 (Vision-Language)
- Encoder: `florence_encoder.onnx` (~173MB)
- Decoder: `decoder_model.onnx` (~388MB)
- Missing: Vision tower model (pixel-to-embedding converter)
- Without vision tower, cannot process images

## DJVU Format

DjVuLibre is not available as a pip wheel for Python 3.12+ on Windows.
All installation methods attempted and failed:
- `djvulibre-python` — no prebuilt wheel
- `djvu2pdf` — failed to install
- SourceForge/GitHub downloads — network issues
- Manual chunk parsing — no readable text chunks found

Workaround: render DjVu pages to PNG via alternative tools, then process with OCR + vision models.