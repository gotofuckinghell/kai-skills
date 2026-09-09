#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Толерантно извлечь markdown из саммари субагентов делегации и объединить в один дистиллят.

Usage:
  python extract_summaries.py OUT.md FILE1 [FILE2 ...]

Каждый FILE — cache/delegation/subagent-summary-N-<timestamp>.txt; порядок аргументов =
порядок задач в диспатче. Из каждого извлекается markdown из JSON-обёртки:
json.loads целиком -> ```json-фенс -> от первого { до последнего }.
Затем разэкранировать \\n, снять фенсы, схлопнуть 3+ пустых строк.
В stdout — размер каждой части и итога (лимит SKILL.md = 100К символов).
"""
import json, re, sys


def extract_md(raw: str):
    try:
        d = json.loads(raw)
        if isinstance(d, dict) and isinstance(d.get('markdown'), str):
            return d['markdown']
    except Exception:
        pass
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.S)
    if m:
        try:
            d = json.loads(m.group(1))
            if isinstance(d, dict) and isinstance(d.get('markdown'), str):
                return d['markdown']
        except Exception:
            pass
    a, b = raw.find('{'), raw.rfind('}')
    if a >= 0 and b > a:
        try:
            d = json.loads(raw[a:b + 1])
            if isinstance(d, dict) and isinstance(d.get('markdown'), str):
                return d['markdown']
        except Exception:
            pass
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out, parts = sys.argv[1], []
    for path in sys.argv[2:]:
        raw = open(path, encoding='utf-8', errors='ignore').read()
        md = extract_md(raw)
        if md is None:
            print('FAILED (no markdown found):', path)
            sys.exit(2)
        md = md.replace('\\n', '\n')
        md = re.sub(r'^```(?:json)?\s*|\s*```$', '', md.strip())
        parts.append(md)
        print(f'OK {len(md):>7} chars: {path}')
    body = '\n\n---\n\n'.join(parts)
    body = re.sub(r'\n{3,}', '\n\n', body)
    open(out, 'w', encoding='utf-8').write(body)
    print(f'combined {len(body)} chars -> {out}')


if __name__ == '__main__':
    main()
