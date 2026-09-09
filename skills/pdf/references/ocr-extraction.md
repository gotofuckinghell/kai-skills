# OCR & Document Text Extraction (merged from the ocr-and-documents skill)

Scripts referenced below live in this skill's scripts/ directory.
# PDF & Document Extraction

For DOCX: see the `docx` skill (create/edit) or use `python-docx` for structured reads.
For PPTX: see the `powerpoint` skill (full create/read/edit support).
For PDF manipulation (merge, split, forms, watermarks, creation): see the `pdf` skill.
This skill covers **text extraction from PDFs and scanned documents**.

> **Coming from a `read_file` EXTRACTION COVERAGE WARNING?** `read_file` auto-converts local PDFs but reads the text layer only; the warning footer lists the pages that yielded no text (scanned images). For a handful of pages, render + vision is fastest: `pdftoppm -jpeg -r 150 -f N -l N file.pdf /tmp/page` then `vision_analyze` each image. For bulk OCR of many pages, use marker-pdf below (Step 2).

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)

---

## Standalone Image OCR (JPG/PNG) — easyocr

For **individual image files** (not PDFs) — e.g., photos of equipment panels, DRO (Digital Readout) displays, screenshots of HMI screens — use `easyocr`. This bypasses the PDF wrapper entirely and works directly on image files.

### Install (Windows MSYS bash — tesseract binary often unavailable)

`pytesseract` Python wrapper is commonly present but the **tesseract binary is not installed** and `winget`/`apt-get` often fail in MSYS. Use easyocr as a drop-in replacement:

```bash
uv pip install easyocr
```

No tesseract binary needed — easyocr bundles its own detection + recognition models.

### Basic usage

```python
import easyocr
from PIL import Image
import numpy as np

reader = easyocr.Reader(['en'], gpu=False, verbose=False)
img = Image.open('photo.jpg')
arr = np.array(img)
results = reader.readtext(arr, detail=0)  # detail=0 → strings only
text = ' '.join([t for t in results if len(t.strip()) > 1])
print(text)
```

### Pitfalls & fixes (learned 2026-08-31)

| Problem | Symptom | Fix |
|---------|---------|-----|
| **DecompressionBombWarning** | `Image size (N pixels) exceeds limit of 89478485` | `from PIL import ImageFile; ImageFile.LOAD_TRUNCATED_IMAGES = True` + `Image.MAX_IMAGE_PIXELS = None` |
| **Image too large for easyocr** | `Invalid input type` or crash at >178Mpx | Downscale: `img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)` where `scale = (4_000_000/(w*h))**0.5` |
| **Tall/narrow screenshots** (HMI scroll captures) | Single strip contains unreadable compressed text | Split into horizontal strips of ~2000–3000px height, OCR each strip, concatenate |
| **MSYS bash `&` backgrounding** | `Foreground command uses '&' backgrounding` error | Use `terminal(background=true, ...)` tool parameter — **do NOT** use `&` or `&>` in bash command strings |
| **Output path `/tmp/...`** | `FileNotFoundError: [Errno 2] No such file or directory: '/tmp/...'` | Use Windows-native absolute paths like `C:/Users/Administrator/Desktop/Stolle/OCR_results.txt` |
| **Pip not found** | `No module named pip` | Use `uv pip install` instead of `pip install` |
| **Slow on CPU** | ~2–5 min per image | Set `gpu=False` explicitly (avoid wasted GPU discovery); models cached after first download |

### Batch processing many JPGs

```python
import easyocr, glob, os, gc
from PIL import Image
import numpy as np

reader = easyocr.Reader(['en'], gpu=False, verbose=False)
jpg_files = sorted(glob.glob('/path/to/folder/*.jpg'))

results = []
for idx, f in enumerate(jpg_files):
    img = Image.open(f)
    w, h = img.size
    if w * h > 4_000_000:
        scale = (4_000_000 / (w*h)) ** 0.5
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    arr = np.array(img)
    text = ' '.join(reader.readtext(arr, detail=0))
    results.append(f'=== {f} ===\n{text}\n')
    if (idx+1) % 20 == 0:
        gc.collect()

# Use a Windows-native absolute path, NOT /tmp/...
out = 'C:/Users/Administrator/Desktop/Stolle/OCR_results.txt'
with open(out, 'w', encoding='utf-8') as f:
    f.write('STOLLE CONCORD - JPG OCR RESULTS\n')
    for r in results:
        f.write(r + '\n')
```

### PNG with strip splitting (for tall scrolling screenshots)

```python
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
import easyocr, numpy as np, glob

reader = easyocr.Reader(['en'], gpu=False, verbose=False)

def ocr_png_strip(f, strip_h=2000):
    img = Image.open(f)
    w, h = img.size
    results, y = [], 0
    while y < h:
        strip = img.crop((0, y, w, min(y+strip_h, h)))
        sw, sh = strip.size
        if sw * sh > 4_000_000:
            sc = (4_000_000/(sw*sh))**0.5
            strip = strip.resize((int(sw*sc), int(sh*sc)), Image.LANCZOS)
        arr = np.array(strip)
        text = ' '.join(reader.readtext(arr, detail=0))
        if text.strip():
            results.append(f'-- y={y} --\n{text[:1000]}')
        y += strip_h
    return '\n'.join(results)

for f in sorted(glob.glob('*.png')):
    print(f'\n===== {f} =====')
    print(ocr_png_strip(f))
```

### Save results to the user's project folder, not /tmp

The user often wants OCR output saved alongside their source files (e.g., `C:/Users/Administrator/Desktop/Stolle/OCR_results.txt`) so it persists and is easy to find. Use Windows-style paths and `encoding='utf-8'` (easyocr results contain non-ASCII).
