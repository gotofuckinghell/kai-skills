#!/usr/bin/env python3
"""OCR every page of a PDF and print the text, page by page.

Purpose: extract searchable text from image-based PDFs (e.g. browser
print-to-PDF of a Feishu/Notion doc, scanned pages) where pymupdf's
get_text() returns nothing.

Dependencies (offline, no tesseract binary required):
    uv pip install pymupdf rapidocr-onnxruntime

Usage:
    python ocr_pdf.py "path/to/file.pdf"
    python ocr_pdf.py "file.pdf" 150        # dpi override (default 150)

Notes:
- rapidocr-onnxruntime downloads its ONNX models to ~/.cache on first run.
- 150 dpi is a good speed/accuracy balance. Bump to 200-300 for small or
  dense text; lower to 100 to speed up large batches.
- Chinese/Japanese/Korean text works out of the box (RapidOCR is
  multilingual); no language flag needed.
"""

import sys

import numpy as np
import pymupdf
from rapidocr_onnxruntime import RapidOCR


def ocr_pdf(path: str, dpi: int = 150) -> None:
    ocr = RapidOCR()
    doc = pymupdf.open(path)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=dpi)
        # pix.samples is raw RGB(A) bytes; reshape to HxWxN
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        if pix.n == 4:  # drop alpha
            img = img[:, :, :3]
        result, _ = ocr(img)
        print(f"===== PAGE {i} =====")
        if result:
            for line in result:
                # RapidOCR line = [box, text, score]; text is [1]
                print(line[1])
        else:
            print("(no text detected)")
        print()
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    _dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    ocr_pdf(sys.argv[1], _dpi)
