#!/usr/bin/env python3
"""GPU-accelerated OCR via RapidOCR + DirectML.

Install:
    uv pip install onnxruntime-directml rapidocr-onnxruntime pymupdf pillow numpy

Usage:
    python extract_rapidocr_dml.py --smoke
    python extract_rapidocr_dml.py <file.pdf> [more files...]
    python extract_rapidocr_dml.py --batch <pdf_dir> <out_dir>
"""
import os, sys, time, json, glob
import fitz
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
ocr = RapidOCR(providers=providers)


def ocr_pdf(pdf_path, out_dir=None, pages=3, dpi=150):
    results = []
    doc = fitz.open(pdf_path)
    for pn in range(min(pages, doc.page_count)):
        pix = doc[pn].get_pixmap(dpi=dpi)
        img_path = os.path.join(out_dir, f'p{pn}.png') if out_dir else None
        if img_path:
            pix.save(img_path)
        img_np = np.array(Image.open(img_path) if img_path else pix)
        r, elapse = ocr(img_np)
        total = sum(elapse) if isinstance(elapse, list) else elapse
        txt = ' '.join([l[1] for l in r]) if r else ''
        results.append({'page': pn+1, 'text': txt, 'time_s': total})
    doc.close()
    return results


def batch_with_checkpoint(pdf_dir, out_dir, pages=3, dpi=150):
    os.makedirs(out_dir, exist_ok=True)
    results_file = os.path.join(out_dir, 'ocr_results.json')

    if os.path.exists(results_file):
        with open(results_file) as f:
            results = json.load(f)
        done = {r['file'] for r in results}
        print(f'Resuming: {len(done)} done')
    else:
        results, done = [], set()

    pdfs = sorted(glob.glob(os.path.join(pdf_dir, '**/*.pdf'), recursive=True))
    print(f'PDFs: {len(pdfs)}, Done: {len(done)}')

    t0 = time.time()
    for pi, pdf in enumerate(pdfs):
        fname = os.path.basename(pdf)
        if fname in done:
            continue
        try:
            doc = fitz.open(pdf)
            page_texts = []
            for pn in range(min(pages, doc.page_count)):
                pix = doc[pn].get_pixmap(dpi=dpi)
                img = os.path.join(out_dir, f'p{pi:04d}_{pn}.png')
                pix.save(img)
                r, _ = ocr(np.array(Image.open(img)))
                if r:
                    page_texts.append(' '.join([l[1] for l in r]))
            doc.close()
            results.append({'file': fname, 'path': pdf, 'text': ' | '.join(page_texts)[:500]})
            done.add(fname)
        except Exception as e:
            results.append({'file': fname, 'text': f'ERROR: {e}'})
            done.add(fname)

        if (pi+1) % 10 == 0:
            elapsed = time.time() - t0
            rate = len(done) / elapsed
            rem = (len(pdfs) - len(done)) / rate if rate else 0
            print(f'{len(done)}/{len(pdfs)} ({elapsed:.0f}s, ~{rem:.0f}s left)')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'DONE. {len(results)} files in {time.time()-t0:.0f}s')


def smoke():
    import onnxruntime as ort
    print('ORT version:', ort.__version__)
    print('Providers:', ort.get_available_providers())
    test = np.zeros((100, 400, 3), dtype=np.uint8)
    r, elapse = ocr(test)
    total = sum(elapse) if isinstance(elapse, list) else elapse
    print(f'Smoke test: {len(r) if r else 0} blocks in {total:.2f}s')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] in {'-h', '--help'}:
        print(__doc__)
        sys.exit(0)
    if args[0] == '--smoke':
        smoke()
    elif args[0] == '--batch' and len(args) > 1:
        batch_with_checkpoint(args[1], args[2] if len(args) > 2 else './ocr_out')
    else:
        for path in args:
            print(f'\n=== {os.path.basename(path)} ===')
            for r in ocr_pdf(path):
                print(f'[p{r["page"]} {r["time_s"]:.2f}s] {r["text"][:200]}')
