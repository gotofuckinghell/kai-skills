# Russian Language OCR: What Works and What Doesn't

## The Problem

RapidOCR (the GPU-accelerated ONNX engine) **does not support Russian**. It only has models for Chinese (`ch_sim`) and English. Attempting to pass `lang='ru'` silently fails — the engine falls back to its default model and produces garbled output where Cyrillic letters are rendered as visually similar Latin characters (e.g., `A.OXHNCKH` instead of `А.ОХИНСКИЙ`).

## What Actually Works for Russian

| Approach | Install | Speed | Quality | Notes |
|----------|---------|-------|---------|-------|
| **Florence-2** (microsoft/Florence-2-base) | HF cache (~400MB) | ~1s/page | High, no hallucinations | Load with `AutoModelForCausalLM.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True)`. **Use the model ID string, NOT a local path.** Local cache: `C:/Users/Administrator/AppData/Local/hermes/cache/hf/models--microsoft--Florence-2-base/snapshots/<hash>/` |
| **PaddleOCR v3** | `uv pip install paddlepaddle paddleocr` | ~1-3s/page | Good | API changed in v3: `use_angle_cls` → `use_textline_orientation`; `use_gpu` removed; `show_log` removed. **Requires `paddlepaddle` separately** — the `paddleocr` pip package alone is not enough. Init: `PaddleOCR(use_textline_orientation=True, lang='ru')`. |
| **Tesseract + pytesseract** | OS package + Python | ~2-5s/page | Medium | Install `tesseract` binary, ensure `tesseract --list-langs` includes `rus`. |
| **marker-pdf** | ~3-5GB | ~1-14s/page CPU | Very high | Full pipeline with Russian. See `ocr-and-documents` skill. |

## Quick Diagnostic

```python
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
result, _ = ocr('russian_page.png')
if result:
    text = '\n'.join([line[1] for line in result])
    print(text)
# If output has Latin-lookalike Cyrillic -> RapidOCR is wrong engine
# Correct: 'А.ОХИНСКИЙ' not 'A.OXHNCKH'
```

## User Context (2026-09)

Russian DJVU book ("222 проблемы с компьютером и их решение"). Rendered pages: `F:/!Для чайников/222 проблемы с компьютером и их решение/rendered_pages/` (20 PNG pages). PDF text was garbled due to encoding issues — not an OCR failure.