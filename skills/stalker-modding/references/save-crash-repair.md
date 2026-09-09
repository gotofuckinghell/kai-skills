# Save-crash repair & pSettings architecture (Clear Sky, verified 2026-09)

## Diagnostics — fastest paths
1. Game-root `XRayEngine_error_report_<MMDDYY-HHMMSS>.zip` (BugTrap) contains `errorlog.log` (header: "xrCore.dll at ... xrDebug::backend()+164" = engine FATAL breakpoint, then the FATAL ERROR block with Expression/Function/File/Line/Arguments) plus the full `xray_<user>.log`. Best source of assert text. This game produces one zip per crash.
2. `$app_data_root$/logs/xray_<user>.log` — overwritten at every launch; after a hard crash it may be 0 bytes (buffered output lost). A CLI run that reaches the crash writes the FATAL before dying.
3. Minidumps `logs/xray_<user>_<date>.mdmp`: parse with pip package `minidump` (`uv venv mdmp_env && uv pip install --python mdmp_env/Scripts/python.exe minidump`). Signature: exception code 0x80000003 (breakpoint) in xrCore ~+0x1B944 = `xrDebug::backend()` — engine FATAL/R_ASSERT, same for every assert. The message text may survive as readable fragments in thread-stack memory segments (read them straight from the file via segment start_file_address + size; strings "Function/File/Arguments", section names). Sometimes the full section name is NOT recoverable from the mdmp (format string lives in module .rdata, not captured) — use the log/zip instead.
4. Reproduce: `cd "<game>/bin" && ./xrEngine.exe -load <savename>` (background + watch log). A game window appears on the user's desktop — warn them. Kill leftovers with `taskkill /F /IM xrEngine.exe`. Success markers: `Game X is successfully loaded`, `Клиент: Синхронизация...`.

## Crash taxonomy (FATAL texts actually seen)
- `CInifile::r_section / Xr_ini.cpp:443 — Can't open section 'X'` — an object (from save load or runtime spawn) references a section missing from pSettings. Save load dies on the FIRST such object in the save's object order; after fixing it, the next missing section surfaces (iterate). Same FATAL mid-game when an NPC interaction renders a stale saved task: random bring-item tasks (CBringItemTask in task_objects.script, lists in misc/bring_item_task.ltx — vanilla only asks vodka/bandage/medkit/bread/antirad/grenades/wpn_sig550) store requested section names; task text rendering calls system_ini():r_string(item,'inv_name'). Real case: «взять квест у командира группы» → `Can't open section 'esc_quest_magic_vodka'` (SoC item from a long-removed mod; fixed by vodka-clone section). Stale-task/object names sit in the COMPRESSED part of the .sav — raw grep of the .sav returning 0 is NOT proof of absence (gar_quest_wpn_pm also had 0 hits while present in an NPC inventory).
- `CInifile::r_section / Xr_ini.cpp:443 — Can't open section 'up_gr_*_<item>'` — missing upgrade-BRANCH definition, NOT a missing object. Item sections carry `upgrades = up_gr_ab_X, up_gr_cd_X, up_gr_ef_X, up_gr_gh_X` (paired-slot scheme, vanilla CS); the branches must be DEFINED as `[up_gr_*]` headers in the loaded upgrade files (armor: misc/outfit_upgrades/o_<armor>_up.ltx; weapons: weapons/upgrades/w_*_up.ltx). When those sibling files come from a different mod generation (single-letter scheme up_gr_a..g only — mismatch is partial: up_gr_g resolves while ab/cd/ef do not), ANY item of that type FATALs when the save recreates it (dies at save select/load). Per-section iteration surfaces only one armor at a time — audit ALL references at once: parse every `upgrades =` in outfit.ltx / w_*.ltx and diff against every `[up_gr_*]` header in outfit_upgrades/*.ltx / weapons/upgrades/*.ltx (scripts/audit_upgrade_refs.py). Fix = restore the CANONICAL file from configs.db (payloads stored uncompressed, byte-range extract; verify the db copy defines the needed branches before writing; .bak the bad file first) — db's vanilla o_*.ltx use the paired names and agree with vanilla outfit.ltx. Never fix by cloning the item section or hand-writing branch sections. Real case: hand-applied SRP install left 4 light-armor files (bandit/novice/cs_light/svoboda_light) in single-letter versions; one db-restore pass fixed all four, weapons side was already consistent.
- `CInifile::r_string/r_float / Xr_ini.cpp:453 — Can't find variable V in [X]` — engine strictly reads a key the section lacks. Real case: `additional_inventory_weight in [af_compass]` — CArtefact::Load does r_float("additional_inventory_weight") for every spawned artefact; vanilla af_compass is class SCRPTART and never exists as a real inventory object, so the key is absent. Fix: add `additional_inventory_weight = 0` to the section (can_be_controlled comes from af_base).
- `CInifile::Load / Xr_ini.cpp:332 — Duplicate section 'X' found` — same section header twice in the loaded set. Engine refuses to start. Dedupe the file.
- `CScriptEngine::lua_error — LUA error: <file>:<line> ...` — runtime Lua crash. Real case: `bind_anomaly_zone.script:75: attempt to index local 'art' (a nil value)`.
- `CPhraseDialog::SayPhrase — No available phrase to say, dialog[esc_trader_meet]` — vanilla: save made while a dialog was active; loading it asserts. Not mod-related. (Workaround if persistent: give the dialog an unconditional fallback phrase.)

## pSettings architecture
- pSettings = system.ltx include tree (48 includes). Only files reachable through includes exist.
- `misc\quest_items.ltx` is included once from system.ltx → a gamedata copy fully replaces the db copy; extra sections appended there land in pSettings. (Appending clone sections there is the standard repair vehicle.)
- creatures: system.ltx → creatures/monsters.ltx (13 files: flesh, bloodsucker, dog, boar, pseudodog, giant, controller, poltergeist, snork, crow, tushkano, phantom, rat) + creatures/stalkers.ltx. **m_burer.ltx, m_zombie.ltx, m_cat.ltx, m_fracture.ltx, m_chimera.ltx are NOT included** → those species and ALL their base/variant sections (m_burer_e, burer_normal, zombie_normal, cat, fracture) are absent from pSettings and cannot be spawned at all. SoC lists offering burer_weak/normal, zombie_trup2, bloodsucker_marsh (CS bloodsuckers: weak/normal/strong/mil/fast/jumper/night_king/redforest only), cat_*, fracture_*, veh_* will always "Can't open section".
- Weapon upgrades: weapon sections carry `upgrades = up_gr_ab_pm, up_gr_cd_pm, ...` (scheme sections defined in weapons/upgrades/w_<name>_up.ltx, reached via misc/inventory_upgrades.ltx → item_upgrades.ltx). Old GSC names encode paired slots (ab, cd); a weapons overhaul mod rewrites w_*.ltx lists (e.g. `up_gr_a_pm, up_gr_b_pm...`) AND the w_*_up.ltx files → old paired names unresolvable. Clones copied from a db w_*.ltx carry the old list → creating the object FATALs "Can't open section 'up_gr_ab_pm'". Rule: source the `upgrades` line from the live (gamedata-overridden) donor; drop the line if the live donor has none.
- Item sections carry `class = II_MEDKI / WP_AK74 / D_PDA / AMMO / D_ELITE...`; monster class lives in the ancestor chain (boar_weak → m_boar_e). Class determines engine object type on creation.

## Repair recipe (save references a section that doesn't exist)
1. Get the exact missing name from the FATAL (zip/log). Iterate: only the first missing section is reported per load.
2. Pick the CS donor closest in semantics (medkit-ish → [medkit], detector → detector_elite, SoC quest wpn → the same-named CS wpn, e.g. gar_quest_wpn_wincheaster1300 → wpn_wincheaster1300).
3. Append to gamedata/configs/misc/quest_items.ltx: marker comment + header line `[newname]:<donor parent...>` + the donor's FULL body (all keys incl. $spawn, class, visual, inv_name, cost). Duplicate $spawn paths across clones are harmless (level-editor only). cp1251 + CRLF.
4. Weapon clones: copy/sync the `upgrades` line from the LIVE donor in gamedata (see above); if absent there, remove the line from the clone.
5. Artefact clones / SCRPTART sections that will become real objects: ensure CArtefact::Load keys exist (additional_inventory_weight etc.) — easiest: inherit/copy from a normal artefact base.
6. Test with CLI `-load`; iterate until "successfully loaded".
7. Result: the saved object now exists as the donor clone — player can use/sell/drop it (flags inherit from donor body).

## Lua crash fix (bind_anomaly_zone.script)
Vanilla update() loops `artefact_ways_by_id`, does `art = alife():object(k)` and dereferences art unconditionally → crash when a zone-spawned artefact left alife without on_artefact_take (destroyed in anomaly etc.). Fix (installed in gamedata/scripts):
```
local dead_ways = {}
for k,v in pairs(artefact_ways_by_id) do
    local cl_pos = (db.storage[k] and db.storage[k].object and db.storage[k].object:position())
    local art = alife():object(k)
    if art == nil then
        dead_ways[#dead_ways+1] = k
    elseif cl_pos ~= nil then ... else ... end
end
for _,k in ipairs(dead_ways) do artefact_ways_by_id[k] = nil end
```
Never delete keys inside pairs(). When editing Lua: strip `--` comments and quoted strings, count keywords vs `end`, and compare the result against the VANILLA file (naive counters return nonzero on vanilla too — compare deltas, not absolute zero). Keep cp1251/CRLF.

## Editing pitfalls (bit twice in one session)
- CRLF + `^\[.*\]\s*$` + re.M → zero matches. Use `$` right after `]` or strip lines.
- Multi-block removal: skip-until-next-`[` must not swallow the marker comment of the FOLLOWING block; after any edit re-scan headers for duplicates (engine FATALs Duplicate section).
- Appends to an already-edited ltx: ensure the file ends with the EOL before joining new blocks.

## User game state (2026-09, GOG CS)
- Game: C:\games\S.T.A.L.K.E.R. Clear Sky; "Launch S.T.A.L.K.E.R. Clear Sky.lnk" is a GOG shortcut to bin/xrEngine.exe (same exe as CLI tests). App data/logs: C:\Users\Administrator\Documents\Stalker-STCS.
- Installed mods beyond ours: weapon-upgrade overhaul (gamedata/configs/weapons/w_*.ltx AND weapons/upgrades/w_*_up.ltx rewritten, 21 files), spawn menu in gamedata/scripts/ui_si.script (SoC/ТЧ name tables incl. veh_*, weak/normal/strong monsters, quest items — spawns via alife():create), god.script ("GOD of the zone v3.0", hotkeys H/J/N/M + spawn_item_in_inv), anom.script, ui_teleport.script.
- Installed fixes (all under gamedata/): 18 SoC-item clone sections + af_compass additional_inventory_weight in misc/quest_items.ltx & artefacts.ltx; bind_anomaly_zone.script nil-guard. Trade mod (17 files in configs/misc) + quest-relief flags from earlier sessions also active.
- NEVER disable/remove a clone section once objects with it may exist in saves. gar_quest_wpn_pm was first disabled (old vanilla upgrade scheme) → every dialog/trade with the NPC owner then FATALed at load-of-inventory; it was re-added in place as a clone of the LIVE modded [wpn_pm] (parent chain default_weapon_params, upgrades up_gr_a_pm..h_pm) and that fixed the dialog crash. Rule: fix the clone with live-donor parents/upgrades; never take it out of quest_items.ltx.
- esc_quest_magic_vodka restored as clone of [vodka] (stale bring-item task in saves).
- outfit.ltx protection boost (2026-09): exo_outfit & svoboda_exo_outfit all protections ×1.5 (physical 0.56→0.84), scientific_outfit («СЕВА») ×1.8 (0.3→0.54); bones_koeff_protection and sect_*_immunities untouched.
- Broken/inapplicable clones removed or disabled: burer_weak/burer_normal/zombie_trup2 (parents not in pSettings), bloodsucker_marsh (duplicate-section issue). Do not re-add unless the whole parent chain and upgrade scheme are verified. (gar_quest_wpn_pm is NOT in this list anymore — see above: re-added as live-donor clone once it turned out to exist in saves.)
