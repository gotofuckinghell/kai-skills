"""Extract full text from a PDF into a file with '===== PAGE N =====' markers,
then print line numbers of topic headings (ТЕМА/ЛЕКЦИЯ patterns) for mapping
lecture boundaries before delegating distillation.

Usage: python extract_book_text.py "<book.pdf>" "<out>.txt"
"""
import re
import sys

import pymupdf

HEADING_PATTERN = r'ТЕМА\s*\d|ЛЕКЦИ[ЯИ]|^\s*Тема\s*\d'


def extract(pdf: str, out: str) -> str:
    doc = pymupdf.open(pdf)
    chunks = []
    for i in range(doc.page_count):
        chunks.append(f'\n===== PAGE {i + 1} =====\n' + doc[i].get_text())
    text = ''.join(chunks)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print('pages:', doc.page_count, 'chars:', len(text), '->', out)

    cur_page = 0
    for n, line in enumerate(text.split('\n')):
        s = line.strip()
        m = re.match(r'===== PAGE (\d+) =====', s)
        if m:
            cur_page = int(m.group(1))
        elif re.search(HEADING_PATTERN, s) and len(s) < 130 and '...' not in s:
            print(f'line {n} (page {cur_page}): {s[:100]}')
    return out


if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])
