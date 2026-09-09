---
name: gpu-ocr-pipeline
description: "GPU OCR on Intel Arc / AMD Radeon using DirectML."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, windows, macos]
metadata:
  hermes:
    tags: [ocr, gpu, directml, intel-arc, amd-radeon, rapidocr, pymupdf, batch]
---

# GPU-Accelerated OCR Pipeline (Intel Arc / AMD Radeon)

For machines without NVIDIA GPUs. Uses Microsoft DirectML with ONNX Runtime — works on Intel Arc (A770/A750/A380), AMD Radeon, and any DirectX 12-capable GPU.

## Why This Stack (Not Others)

- `easyocr` + `torch-directml` → **fails** (CUDA runtime calls)
- `paddlepaddle-gpu` → **fails** (CUDA-only, silent CPU fallback)
- `onnxruntime` (default) → **no GPU** (CPU/Azure only)
- `onnxruntime-directml` + `rapidocr-onnxruntime` → **works** (~1.5–3 sec/page on Intel Arc A770)

## Install

```bash
uv pip install onnxruntime-directml rapidocr-onnxruntime pymupdf pillow numpy
```

**Critical**: install `onnxruntime-directml`, not plain `onnxruntime`.

## Quick Start

```python
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
ocr = RapidOCR(providers=providers)

img = np.array(Image.open('page.png'))
result, elapse = ocr(img)
if result:
    text = ' '.join([line[1] for line in result])
```

## OCR a PDF (render + RapidOCR)

```python
import fitz, os, numpy as np
from PIL import Image

def ocr_pdf(pdf_path, out_dir, pages=3, dpi=150):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    doc = fitz.open(pdf_path)
    for pn in range(min(pages, doc.page_count)):
        pix = doc[pn].get_pixmap(dpi=dpi)
        img_path = os.path.join(out_dir, f'p{pn}.png')
        pix.save(img_path)
        r, elapse = ocr(np.array(Image.open(img_path)))
        total = sum(elapse) if isinstance(elapse, list) else elapse
        txt = '\n'.join([l[1] for l in r]) if r else ''  # join with newline for multi-line pages
        results.append({'page': pn+1, 'text': txt, 'time_s': total})
    doc.close()
    return results
```

**Pitfall**: `elapse` is a **list** (per-stage timings). Use `sum(elapse)`. Doing `f"{elapse:.2f}"` on a list raises `TypeError`.

## Batch with Checkpointing

See `scripts/extract_rapidocr_dml.py`.

## Verify Stack Before Batch

```bash
python scripts/extract_rapidocr_dml.py --smoke
```

## Cleanup (When Asked)

```bash
uv pip uninstall easyocr paddlepaddle-gpu
```
Keep: `onnxruntime-directml`, `rapidocr-onnxruntime`, `pymupdf`, `pillow`, `numpy`.

## Russian Language OCR — Critical Pitfall

**RapidOCR does NOT support Russian.** It only supports `ch_sim` (simplified Chinese) and English. Passing `lang='ru'` or `params={'Rec.lang': 'ru'}` has no effect — it silently falls back to its default model and produces gibberish (Cyrillic rendered as lookalike Latin characters, e.g. `A.OXHNCKH` instead of `А.ОХИНСКИЙ`).

If you need Russian OCR, use one of these:

| Tool | Status | Notes |
|------|--------|-------|
| **Florence-2** (microsoft/Florence-2-base) | ✅ Works | Load with `trust_remote_code=True`. **Use the model ID string, NOT a local filesystem path** — `AutoModelForCausalLM.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True)`. Local cache: `C:/Users/Administrator/AppData/Local/hermes/cache/hf/models--microsoft--Florence-2-base/snapshots/<hash>/`. |
| **PaddleOCR v3** | ⚠️ Partial | API changed in v3: `use_angle_cls` → `use_textline_orientation`; `use_gpu` parameter removed entirely; `show_log` removed. Init: `PaddleOCR(use_textline_orientation=True, lang='ru')`. **Requires `paddlepaddle` package separately** — `uv pip install paddlepaddle` first, otherwise import fails silently. |
| **Tesseract + pytesseract** | ✅ Works | Install `tesseract` binary, ensure `tesseract --list-langs` includes `rus`. |
| **marker-pdf** | ✅ Works | Full OCR with Russian support (~3-5GB install). See `ocr-and-documents` skill. |

Quick diagnostic: if OCR output contains Latin-lookalike Cyrillic (`A.OXHNCKH` instead of `А.ОХИНСКИЙ`), the engine is wrong for this task.

## Benchmark (Intel Arc A770 4GB)

| Input | Time |
|-------|------|
| 4576x3432 JPG | ~1.54 sec |
| 1772x1263 PNG | ~2.90 sec |
| easyocr CPU | ~6.7 sec |

Speedup: ~4.3x vs CPU.
