#!/usr/bin/env python3
"""compare_patch_md5.py <patch.zip> [<gamedata-root>]

Which on-disk gamedata files are actually the patch's versions?
md5-compare every gamedata/configs/**.ltx inside the patch zip against the
disk. Files that MATCH the zip are patch-owned regardless of their file
timestamps (patch archives preserve original dates — dates do NOT diagnose
overwrites). Files that differ are user mods / manual edits still alive.

Default gamedata root: C:/games/S.T.A.L.K.E.R. Clear Sky/gamedata
Exit code 0 always; prints a summary + the differing (still-mine) files.
"""
import sys, os, zipfile, hashlib, collections

def md5(b):
    return hashlib.md5(b).hexdigest()[:10]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    zpath = sys.argv[1]
    gd = sys.argv[2] if len(sys.argv) > 2 else r'C:/games/S.T.A.L.K.E.R. Clear Sky/gamedata'
    z = zipfile.ZipFile(zpath)
    by_path = {}
    for i in z.infolist():
        n = i.filename
        if n.startswith('gamedata/') and n.endswith('.ltx'):
            rel = n[len('gamedata/'):]
            try:
                by_path[rel] = md5(z.read(i))
            except Exception:
                pass
    stats = collections.Counter()
    mine = []
    for rel, zh in sorted(by_path.items()):
        disk = os.path.join(gd, rel.replace('/', os.sep))
        if not os.path.exists(disk):
            stats['in zip, missing on disk'] += 1
            mine.append(rel + '  (MISSING ON DISK)')
            continue
        if md5(open(disk, 'rb').read()) == zh:
            stats['patch version on disk'] += 1
        else:
            stats['differs = still yours'] += 1
            mine.append(rel)
    print('configs compared:', len(by_path))
    for k, v in stats.items():
        print(f'  {k}: {v}')
    print('\nfiles that DIFFER from the patch (user mods/edits):')
    for m in mine:
        print(' ', m)

if __name__ == '__main__':
    main()
