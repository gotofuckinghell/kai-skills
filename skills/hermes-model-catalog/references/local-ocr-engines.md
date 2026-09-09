# Local OCR Engines (PaddleOCR / RapidOCR)

When `marker-pdf` is too heavy (~5GB) and `pymupdf` can't read a scanned document, the user may have a local OCR engine installed directly. This reference covers the two engines seen in practice on this system.

## PaddleOCR 3.x (Russian support)

PaddleOCR supports `lang='ru'` natively and is the recommended choice for Cyrillic OCR.

### Install

```bash
# In the Hermes venv:
uv pip install paddleocr
```

### Correct constructor (PaddleOCR 3.7.0)

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_textline_orientation=True, lang='ru')
result = ocr.ocr('page_001.png')
for line in result[0]:
    print(line[1][0])
```

### Rejected parameters (3.x broke them)

| Parameter | Status |
|-----------|--------|
| `use_angle_cls=True` | Deprecated — replaced by `use_textline_orientation` |
| `use_gpu=False` | Rejected — removed in 3.x |
| `show_log=False` | Rejected — removed in 3.x |

If any of these appear in old code, strip them. The minimal working call is:

```python
PaddleOCR(lang='ru')
```

### Notes

- First run downloads models (~100MB) to `~/.cache/paddleocr/`.
- Output is `[[box, (text, confidence)], ...]` per page.
- Slower than RapidOCR on CPU (~1-3s/page), but the only engine here with real Russian support.

## RapidOCR (no Russian)

```python
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
result, _ = ocr.ocr('page.png')
```

RapidOCR **silently mangles Cyrillic**: it substitutes visually similar Latin glyphs (п→n, о→o, б→6, н→H). It has no `lang='ru'` parameter. Do not use it for Russian documents.

## When to use which

| Scenario | Engine |
|----------|--------|
| Russian text, accuracy matters | PaddleOCR `lang='ru'` |
| Latin text, speed matters | RapidOCR |
| Mixed / unknown | PaddleOCR (auto-detect) |

## Related

- `ocr-and-documents` SKILL.md — pymupdf vs marker-pdf decision tree
- `references/local-ocr-engines.md` — this file

