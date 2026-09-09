# Book Analysis Workflow

Complete pipeline for analyzing books (PDF/DJVU): render pages → OCR text → vision-language captions → output alongside original.

## Quick Reference (Inline Python)

```python
import os, fitz, json
from rapidocr_onnxruntime import RapidOCR
import sys
sys.path.insert(0, r"C:/Users/Administrator/Documents/!LAMA/scripts")
from unified_analyzer import UnifiedImageAnalyzer

# Setup paths
pdf_path = r"F:\path\to\book.pdf"
output_dir = os.path.dirname(pdf_path)
render_dir = os.path.join(output_dir, "rendered_pages")
os.makedirs(render_dir, exist_ok=True)

# 1. Render pages (PyMuPDF CPU-only — user says use GPU next time)
# Note: PyMuPDF fitz.Matrix() is CPU-only. For GPU, use ffmpeg.
doc = fitz.open(pdf_path)
for i in range(min(20, len(doc))):  # Start with 20 pages
    page = doc[i]
    mat = fitz.Matrix(150/72, 150/72)  # 150 DPI
    pix = page.get_pixmap(matrix=mat)
    pix.save(os.path.join(render_dir, f"page_{i:03d}.png"))
doc.close()
print(f"Rendered pages saved to {render_dir}")

# 2. OCR with RapidOCR (GPU via DirectML)
ocr = RapidOCR(['DmlExecutionProvider', 'CPUExecutionProvider'])
ocr_results = []
for f in sorted(os.listdir(render_dir)):
    if not f.endswith('.png'): continue
    page_num = int(f[5:8])
    out = ocr(os.path.join(render_dir, f))
    texts = out[0] if out else None
    el = out[1] if out and len(out) > 1 else 0
    if isinstance(el, list): el = sum(el)  # elapse is list of stage timings!
    text = "\n".join([t[1] for t in texts]) if texts else ""
    ocr_results.append({"page": page_num, "text": text, "blocks": len(texts) or 0, "time": el})
    print(f"Page {page_num}: {len(text)} chars")

with open(os.path.join(output_dir, "ocr_results.json"), 'w', encoding='utf-8') as fh:
    json.dump(ocr_results, fh, ensure_ascii=False, indent=2)

# 3. Vision-language analysis (Florence-2 + MobileNetV2)
analyzer = UnifiedImageAnalyzer()
analysis_results = []
for f in sorted(os.listdir(render_dir))[:10]:  # Sample first 10
    if not f.endswith('.png'): continue
    page_num = int(f[5:8])
    try:
        result = analyzer.analyze(os.path.join(render_dir, f), task="<DETAILED_CAPTION>", max_tokens=80)
        analysis_results.append({
            "page": page_num,
            "caption": result.get("caption", {}).get("caption", "N/A"),
            "class": result.get("classification", {}).get("top1", {}).get("class", "N/A"),
            "confidence": result.get("classification", {}).get("top1", {}).get("confidence", 0)
        })
        print(f"Page {page_num}: {analysis_results[-1]['caption'][:80]}")
    except Exception as e:
        print(f"Page {page_num}: ERROR - {e}")

with open(os.path.join(output_dir, "analysis_results.json"), 'w', encoding='utf-8') as fh:
    json.dump(analysis_results, fh, ensure_ascii=False, indent=2)

print(f"\nDone! Results in {output_dir}")
```

## Key Pitfalls

### `elapse` Is a List, Not a Number
RapidOCR returns `(texts, elapse)` where `elapse` is a **list** of per-stage timings (detection, recognition, etc.). Use `sum(elapse)` or `elapse[0]`. Doing `"{elapse:.2f}s"` on a list raises `TypeError: unsupported format string passed to list.__format__`.

### PyMuPDF Deprecation Warning
`fitz` module shows deprecation warning: "The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead." The import itself still works — warnings don't break functionality.

### CPU Rendering Is Slow
PyMuPDF `fitz.Matrix()` renders on CPU. User explicitly said "рендери при помощи GPU" (render with GPU). For GPU-accelerated rendering, prefer ffmpeg: `ffmpeg -i book.pdf -vf fps=1/5 -q:v 2 page_%03d.jpg`.

### Don't Render All 221 Pages at Once
Start with 20 pages to verify the pipeline works before scaling. Large PDFs = long render + OCR times.

## Output Files Created

| File | Contents |
|------|----------|
| `rendered_pages/` | PNG images at 150 DPI |
| `ocr_results.json` | RapidOCR text extraction |
| `analysis_results.json` | Florence-2 captions + MobileNetV2 classification |
| `book_text.txt` | Combined OCR text |
| `book_analysis.json` | Unified analysis |

## Scripts Location

All working scripts: `C:/Users/Administrator/Documents/!LAMA/scripts/`
