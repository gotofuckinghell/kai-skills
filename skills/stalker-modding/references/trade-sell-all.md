# Trade: «sell everything» / «buy everything» (Clear Sky)

Goal: every named trader sells every real item in the game (artefacts, meds, food, weapons, ammo, outfits, detectors), and generic NPCs buy anything. Recipe verified working; stock refreshes on trader restart (level re-entry / ~24 game hours).

## Architecture facts (verified against files + engine behaviour)

- Each `trade/<file>.ltx` carries its OWN local `[trade_generic_buy]` / `[trade_generic_sell]` sections (bare headers, no `:parent`). Editing `misc/trade_generic.ltx` does NOT propagate to named traders — edit every file (both are part of the pass).
- `misc/trade_generic.ltx` `[trader]` has NO `buy_supplies` — generic stalkers sell only from their own inventory (loot/gear), never a shop stock. Give them stock only if every stalker should be a shop.
- `[trader]` fields are condlists (`{=info_x} secA, secB` — first match wins); `buy_supplies` names point at a chain (`[supplies_good_price]:supplies_start`). Add stock lines to the chain ROOT (no `:parent`) — inheritors see them; but a NO TRADE in a CHILD section overrides a root enable, so bans must be cleared at every chain level.
- NO TRADE lines are bare keys without `=` (`medkit_army ;NO TRADE`). A bare key in a trade section = DISABLE. `item = F, E` = ENABLE.
- Stock line = `item = count, probability`; `= 3, 1.0` guarantees presence.
- Items not mentioned at all are ENABLED at default factor 1.
- `trade_secret_trader_agr_stalker.ltx` has `buy_supplies` COMMENTED OUT (`;buy_supplies = supplies_generic`) — vanilla: buy-only fence. Uncomment to give him a shop.

## Master item list (what «everything» means)

Build from gamedata files only (they are guaranteed in pSettings):
- `misc/artefacts.ltx`: `af_*` (53)
- `misc/items.ltx`: all sections minus `*_hud` (16: medkit*, bandage, antirad, еда, device_pda, dev_flash_*, device_torch, guitar/harmonica — NOT `wpn_vodka_hud`, that is a HUD object)
- `weapons/w_*.ltx`: `wpn_*` minus service variants
- `weapons/*.ltx`: `ammo_*` minus `ammo_base`; `grenade_*` minus `*_hud`
- `misc/outfit.ltx`: sections with `:outfit_base` minus `without_outfit` (14)
- detectors `detector_simple/advanced/elite` — sections live in configs.db but names are confirmed by vanilla trade files

EXCLUDE service weapon sections or the shop gets junk (and spawn of a non-item may FATAL): `_(minigame|up\d*|hud|no_draw_sound|with_scope)$`, `wpn_rpg7_missile`. `*_arena` weapons are NOT in gamedata w_*.ltx (db-only) so they never enter the list — leave their NO TRADE alone. Count sanity: 157 items total (53 af + 39 wpn + 29 ammo + 3 grenades + 14 outfits + 16 items + 3 detectors); w_*.ltx has ~93 `wpn_` headers but only ~39 are real weapons — the rest are `_hud`/minigame/`_up`/spec variants.

## Value conventions per section type

- sell sections (name contains `sell`): enable as `= 1.7, 1.7`
- buy sections: `= 0.5, 0.3` (matches existing buy-all lines)
- supplies/stock sections: `= 3, 1.0`

## Verification after the pass

- No duplicate section headers per file (engine FATALs `Duplicate section 'X' found`).
- No duplicate KEYS inside one section (last-wins is not guaranteed for CPurchaseList — it may spawn twice).
- CRLF intact: bare-LF count must be 0 (`python: data.count(b'\n') - data.count(b'\r\n')`).
- `grep NO TRADE` WILL also match your own `(was NO TRADE)` marker comments — that is a false positive, not a leftover ban; a real ban is a bare key line.
- Diff vs `.bak_sellall`: only added `= ...` lines and removed bare-key lines; section headers untouched.

## Run

`perl scripts/trade_sell_all.pl <gamedata/configs>` then `perl scripts/trade_sell_all_fix.pl <gamedata/configs>/misc` (second pass clears bans inside buy sections and supplies chains). Both create `.bak_sellall*` per file; restore by copying back. Re-run is idempotent (enable lines have `=`, bare-key detection skips them).

Script-writing rules for these passes (Perl on Windows):
- NEVER use glob() on a path containing spaces (Strawberry splits it) — list files with opendir/readdir + regex.
- `split /(\r?\n)/` keeps line endings as separate array elements; skipping an element without pushing it glues two lines together — every branch must push the original or a replacement.
- Build replacement lines with explicit `"\x0d\x0a"`, never a bare `"\n"` (files are CRLF).
- Read/write cp1251 files byte-wise (`<:raw`), add only ASCII comments.
