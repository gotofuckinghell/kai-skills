"""Resolve a Windows .lnk shortcut target path.

Cyrillic LocalBasePath is stored ANSI (cp1251), not UTF-16 — a naive
UTF-16 scan misses it. Works when WScript.Shell is unavailable or
mangles non-ASCII paths.

Usage: python resolve_lnk.py "<path-to>.lnk"
"""
import re
import sys


def resolve(lnk_path: str) -> str | None:
    data = open(lnk_path, 'rb').read()
    # UTF-16LE path strings
    for m in re.finditer(rb'(?:[\x20-\x7e\x80-\xff]\x00){8,}', data):
        s = m.group().decode('utf-16-le', errors='ignore')
        if re.match(r'^[A-Za-z]:\\', s):
            return s.split('\x00')[0]
    # ANSI cp1251 LocalBasePath
    for m in re.finditer(rb'[\x20-\x7e\x80-\xff]{8,}', data):
        s = m.group().decode('cp1251', errors='ignore')
        if re.match(r'^[A-Za-z]:\\', s) and '.' in s:
            return s.split('\x00')[0]
    return None


if __name__ == '__main__':
    print(resolve(sys.argv[1]))
