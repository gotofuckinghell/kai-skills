#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge subagent distillation summaries into one markdown body.

Usage: python merge_distillates.py <summary1> <summary2> ... [-o out.md]

Subagent summaries arrive as JSON {"markdown": ...} but are often wrapped in
prose and/or ```json fences, and after json.loads the markdown still contains
literal backslash-n sequences from double escaping. This script extracts the
markdown (whole-file -> fenced -> first-{ to last-}), replaces literal '\n'
with real newlines, and joins parts with '\n\n---\n\n'.
"""
import json
import re
import sys


def extract_markdown(raw: str):
    # 1) whole file
    try:
        return json.loads(raw).get('markdown')
    except Exception:
        pass
    # 2) fenced json block
    m = re.search(r'```json\s*(\{.*?\})\s*```', raw, re.S)
    if m:
        try:
            return json.loads(m.group(1)).get('markdown')
        except Exception:
            pass
    # 3) first { to last }
    a, b = raw.find('{'), raw.rfind('}')
    if a >= 0 and b > a:
        try:
            return json.loads(raw[a:b + 1]).get('markdown')
        except Exception:
            pass
    return None


def main():
    args = sys.argv[1:]
    out = 'combined_distillate.md'
    if '-o' in args:
        i = args.index('-o')
        out = args[i + 1]
        del args[i:i + 2]
    parts = []
    for p in args:
        raw = open(p, encoding='utf-8', errors='ignore').read()
        md = extract_markdown(raw)
        if md:
            # literal backslash-n from double JSON escaping -> real newlines
            md = md.replace(chr(92) + 'n', chr(10))
            md = re.sub(r'\n{3,}', '\n\n', md)
            parts.append(md)
            print(f'{p}: OK {len(md):,} chars')
        else:
            print(f'{p}: FAILED to extract markdown')
    if parts:
        combined = '\n\n---\n\n'.join(parts)
        open(out, 'w', encoding='utf-8').write(combined)
        print(f'TOTAL {len(combined):,} chars -> {out}')


if __name__ == '__main__':
    main()
