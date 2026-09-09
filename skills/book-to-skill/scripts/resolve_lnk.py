import re, sys

# Resolve .lnk target path (ANSI cp1251). Usage: python resolve_lnk.py <file.lnk>
path = sys.argv[1]
data = open(path, 'rb').read()
for m in re.finditer(rb'[A-Za-z]:\\[\x20-\x7e\x80-\xff]{5,}', data):
    s = m.group().decode('cp1251', errors='ignore')
    if re.search(r'\.[A-Za-z0-9]{2,4}$', s):
        print(s)
        sys.exit(0)
print('NOT FOUND', file=sys.stderr)
sys.exit(1)
