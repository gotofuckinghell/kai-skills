#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from a book file by extension.

Usage: python extract_book_text.py <book_path> <out_dir> [slug]

Formats:
  .pdf  -> pymupdf text layer (per-page '===== PAGE N =====' markers);
           empty pages mean a scan -> render PNGs + ocr_winrt_ru.ps1
  .doc  -> antiword; if it reports 'probably a Rich Text Format file',
           the file is RTF and needs Word COM (below)
  .rtf  -> Word COM (win32com) — do NOT hand-parse RTF on real books

Word COM requires MS Word; check the registry first:
  HKLM\SOFTWARE\...\App Paths\WINWORD.EXE
"""
import os
import re
import subprocess
import sys


def extract_pdf(path):
    import pymupdf
    doc = pymupdf.open(path)
    parts = []
    for i in range(doc.page_count):
        parts.append(f'\n===== PAGE {i + 1} =====\n' + doc[i].get_text())
    doc.close()
    return ''.join(parts)


def extract_doc_antiword(path):
    # native Windows path; git-bash path mangling breaks antiword
    r = subprocess.run(['antiword', '-m', 'UTF-8.txt', path], capture_output=True)
    if r.returncode == 0:
        return r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('cp1251', errors='replace')
    if 'Rich Text Format' in err:
        raise RuntimeError('file is actually RTF -> use Word COM')
    r2 = subprocess.run(['antiword', path], capture_output=True)
    if r2.returncode == 0:
        return r2.stdout.decode('cp1251', errors='replace')
    raise RuntimeError(err[:300])


def extract_via_word(paths):
    """Batch-open .doc/.rtf files in one Word instance; returns {path: text}."""
    import win32com.client as win32
    word = win32.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    out = {}
    try:
        for p in paths:
            doc = word.Documents.Open(p, ReadOnly=True, AddToRecentFiles=False)
            out[p] = doc.Content.Text
            doc.Close(False)
    finally:
        word.Quit()
    return out


def main():
    src, outdir, slug = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    ext = os.path.splitext(src)[1].lower()
    if ext == '.pdf':
        text = extract_pdf(src)
    elif ext == '.doc':
        try:
            text = extract_doc_antiword(src)
        except RuntimeError:
            text = extract_via_word([src])[src]
    elif ext == '.rtf':
        text = extract_via_word([src])[src]
    else:
        raise SystemExit(f'unsupported extension: {ext}')
    outp = os.path.join(outdir, slug + '.txt')
    with open(outp, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'{slug}: {len(text):,} chars -> {outp}')


if __name__ == '__main__':
    main()
