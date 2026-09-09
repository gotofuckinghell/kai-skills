# Clear Sky NPC money: where it lives and how to change it

## Mechanics (from xray-15 source)
- Trader/stock NPCs (`CSE_ALifeTraderAbstract` ctor, xrServerEntities/xrServer_Objects_ALife_Monsters.cpp): `money` field read from the object's own config section, if present.
- Human stalkers: money is OVERWRITTEN at spawn from their profile: `selected_char.MoneyDef()` → `min_money/max_money` (random in range); profile `min=max=0` leaves the section value.
- Profiles are `<specific_character id=...>` entries in `gameplay/character_desc_*.xml` (list of files in section `[profiles]` / `specific_characters_files` — inside configs.db, NOT gamedata). Tag: `<money min="N" max="N" infinitive="0|1"/>` (specific_character.cpp:198).
- `infinitive="1"` = money NEVER decreases: `CInventoryOwner::set_money` does `m_money = _max(m_money, amount)` (InventoryOwner.cpp:587) and the trade UI shows the partner's money as `--- RU`. This is the clean way to let NPCs buy anything from the player — but ALSO raise min/max, because the trade code checks the partner's current money against the price before the deal.

## Recipe: give NPCs millions (applied 2026-09)
1. Extract the 13 `character_desc_*.xml` from configs.db (see references/db-archive-format.md). 63 profiles carry a `<money>` tag; `character_desc_general.xml` (45 tags) holds the random-stalker profiles.
2. Replace every `<money min="\d+" max="\d+" infinitive="\d+"/>` with `<money min="2000000" max="5000000" infinitive="1"/>` (byte-level, cp1251-safe).
3. Write the changed files to `gamedata/configs/gameplay/` — full files, correct names; they override the db.
4. Applies to NPCs spawned after the change (re-enter the level / new save load); money is set at object creation.

Runnable on any baseline (incl. SRP versions of the XML): `perl scripts/npc_money_boost.pl <gamedata/configs/gameplay>` — idempotent, byte-wise cp1251-safe.

## Trade UI boundary (why "Ctrl moves whole stack" is an engine mod)
The trade/actor window is C++ (`CUIActorMenu`, xrGame/ui/UIActorMenu*.cpp, UIDragDropListEx.cpp) — Lua scripts cannot extend it. Stack transfer semantics: `CUICellContainer::RemoveItem(itm, force_root)` pops ONE unit from a stacked cell unless `force_root=true` (UIDragDropListEx.cpp:544); double-click and drag call it with `force_root=false`, so stacks move 1 unit per action and the "move all" buttons call `TransferItems` per list. A Ctrl+click "move whole stack" gesture = ~5 lines in `OnItemDbClick` + full engine rebuild (Visual Studio + legacy DirectX SDK, replace xrGame.dll) — out of scope for config modding.
