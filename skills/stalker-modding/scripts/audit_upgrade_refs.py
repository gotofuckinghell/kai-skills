#!/usr/bin/env python3
"""Audit S.T.A.L.K.E.R. Clear Sky upgrade references vs definitions.

For every `upgrades =` line in outfit.ltx / w_*.ltx, check each referenced
up_gr_* section is DEFINED (as a [up_gr_*] header) among the upgrade files
that must carry it. Missing branches = save-load FATAL
`CInifile::r_section "Can't open section 'up_gr_*'"` for ANY item of that type.

Pairs checked:
    armor:   refs in misc/outfit.ltx          -> misc/outfit_upgrades/*.ltx
    weapons: refs in weapons/w_*.ltx          -> weapons/upgrades/*.ltx

Usage:
    python audit_upgrade_refs.py [game_root | <game>/gamedata/configs]
Exit code 0 = all refs resolve; 1 = at least one missing.
"""
import re, sys, glob, os

DEFAULT = r"C:/games/S.T.A.L.K.E.R. Clear Sky/gamedata/configs"
HDR = re.compile(r"^\[([^\] :]+)(?::([^\]]+))?\]$")


def lines(path):
    return open(path, "rb").read().decode("cp1251", "ignore").split("\r\n")


def group_audit(cfg, label, ref_globs, def_globs):
    """Returns {ref_file: {section: [missing up_gr...]}}."""
    defined = set()
    for g in def_globs:
        for f in glob.glob(os.path.join(cfg, g)):
            for ln in lines(f):
                m = HDR.match(ln.strip())
                if m and m.group(1).startswith("up_gr_"):
                    defined.add(m.group(1))
    missing = {}
    for g in ref_globs:
        for rf in glob.glob(os.path.join(cfg, g)):
            cur = None
            for ln in lines(rf):
                m = HDR.match(ln.strip())
                if m:
                    cur = m.group(1)
                    continue
                if cur is None:
                    continue
                um = re.match(r"^\s*upgrades\s*=\s*(.+?)\s*$", ln)
                if um:
                    refs = [x.strip() for x in um.group(1).split(",") if x.strip()]
                    miss = sorted(r for r in refs if r not in defined)
                    if miss:
                        missing.setdefault(rf, {})[cur] = miss
    return missing


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if os.path.basename(arg.rstrip("/\\")) != "configs":
        arg = os.path.join(arg, "gamedata", "configs")
    if not os.path.isdir(arg):
        print("configs dir not found:", arg)
        sys.exit(2)

    bad = False
    for label, refs, defs in (
        ("ARMOR", ["misc/outfit.ltx"],
         ["misc/outfit_upgrades/*.ltx", "misc/outfit.ltx"]),
        ("WEAPONS", ["weapons/w_*.ltx"],
         ["weapons/upgrades/*.ltx", "weapons/w_*.ltx", "weapons/weapons.ltx"]),
    ):
        res = group_audit(arg, label, refs, defs)
        if not res:
            print(label + ": all upgrade refs resolve")
            continue
        bad = True
        print(label + " — missing up_gr definitions:")
        for rf, secs in res.items():
            for sec, miss in secs.items():
                print(f"  {rf} [{sec}]: {miss}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
