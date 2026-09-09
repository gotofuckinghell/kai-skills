# x-ray 1.5 (Clear Sky) .db archives: format & extraction

Any content NOT present under `gamedata/` lives inside `resources/configs.db` (configs, gameplay XML, scripts) and `resources/resources.db0-2` (levels etc.). gamedata files OVERRIDE db files of the same name/path — mods never edit the db.

## Container format (verified against OpenXRay/xray-15 LocatorAPI.cpp)

Chained chunks `{u32 id}{u32 size}{payload}`:
- chunk **666** (CFS_HeaderChunkID) — small CInifile: `[header] auto_load / entry_point / ...` (often ~158 bytes, plain text right after the 8-byte header)
- chunk **0** — all file data, stored mostly UNCOMPRESSED and contiguous (files appear in plain text, e.g. XML and .ltx readable directly by offset)
- chunk **0x80000001** (high bit = compressed) — the FILE CATALOG, LZHUF-compressed, sits at the very end of the file

Catalog records (after LZHUF decompress): `u16 buffer_size`, then buffer = `u32 size_real, u32 size_compr, u32 crc, char name[name_len], u32 ptr` where `name_len = buffer_size - 16`. `size_real == size_compr` means the file is stored uncompressed at absolute offset `ptr` — cut it out directly. Name includes path prefix `configs\gameplay\...`.

## Extraction toolchain (no xrUnpacker needed)

1. Clone the engine (authoritative for EVERY mechanic question, incl. money/trade/UI):
   `git clone --depth 1 --branch xd_dev https://github.com/OpenXRay/xray-15.git` (~74 MB; sources under `cs/engine/`; grep there instead of guessing).
2. Build the LZHUF catalog decoder from the engine's own code (self-contained after stubbing stdafx):
   - copy `cs/engine/xrCore/LzHuf.cpp`; replace `#include "stdafx.h"` with `typedef unsigned char u8; typedef unsigned int u32; #define IC inline` + malloc/free wrappers for xr_malloc/xr_free/xr_realloc
   - main.cpp: walk chunks, locate catalog chunk 0x80000001, call `_decompressLZ`, parse records (skip u16 size; fields as above)
   - build: `g++ -O2 main.cpp LzHuf.cpp` (MinGW from Strawberry Perl works)
3. Extract: uncompressed files (`real == compr`) = `db_bytes[ptr : ptr+real]`.

## Editing content from the db

1. Extract the FULL file from the db (an override must be complete — the engine reads the file whole; a partial override silently drops every profile/section you omitted).
2. Patch bytes (keep cp1251/CRLF exactly; regex-replace only ASCII tags).
3. Write to the matching gamedata path: db `configs\gameplay\character_desc_general.xml` → `gamedata/configs/gameplay/character_desc_general.xml`.
4. XML supports `#include "gameplay\xxx.xml"` directives inside elements — included files resolve from the same dir; you may override just an included file by name.

## Pitfalls
- LZHUF is NOT zlib; the compressed catalog cannot be read with Python's zlib.
- `#include` names inside XML/text are NOT the db catalog — searching the db for `character_desc_general.xml` finds nothing; names come only from the decompressed catalog (or from `specific_characters_files`-style lists in .ltx).
- grep.app and GitHub code search are rate-limited/authed — for engine lookups clone the repo and grep locally.
