---
name: windows-perl-scripting
description: "Use when writing or running Perl scripts on Windows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [perl, strawberry, windows, git-bash, scripting, cpan]
---

# Perl Scripting on Windows (git-bash + Strawberry)

Writing and running Perl scripts on this Windows host. Two Perls exist:

| Perl | Where | When to use |
|---|---|---|
| git-bash bundled 5.42.2 | `/usr/bin/perl` (inside `hermes\git`) | quick pure-core scripts from bash; `perl -c` first |
| Strawberry 5.42.3 | `C:/Strawberry/perl/bin/perl.exe` | anything needing modules, cpanm, or the system perl (cmd/PowerShell) |

## Running Strawberry from git-bash

- Strawberry is a NATIVE Windows binary: pass `C:/...` paths, never MSYS `/c/...` — a `/c/` arg fails as `Can't open perl script ... No such file or directory` even though the file exists.
- Prep `PATH` with `C:/Strawberry/c/bin` FIRST (`export PATH="/c/Strawberry/c/bin:/c/Strawberry/perl/site/bin:/c/Strawberry/perl/bin:$PATH"`) — Net::SSLeay/IO::Socket::SSL need libssl/libcrypto DLLs from `c\bin`; without them HTTPS and cpanm die with `load_file ... The specified module could not be found`.
- `perl -c script.pl` before every run — a silent syntax break costs a full cycle.

## Pitfalls that corrupt output (each cost a cycle)

- **glob() splits on spaces in paths**: `glob("C:/games/S.T.A.L.K.E.R. Clear Sky/.../*.ltx")` returns path fragments. Never glob a path that may contain spaces — list with opendir/readdir + regex filter.
- **`split /(\r?\n)/` keeps line endings as separate array elements.** Any branch that `next`s without pushing the element glues two lines together — every code path must push the original element or a replacement. Symptom: whole file collapses to one line.
- **New lines in CRLF files must be built with explicit `"\x0d\x0a"`**, never `"\n"` — mixing LF into CRLF files is tolerated by the X-Ray parser but breaks diffs and round-trips.
- **cp1251 config files: work byte-wise** (`<:raw`), write only ASCII comments; the console mangles Cyrillic anyway (cp866/cp1251) — keep script output ASCII or write results to a UTF-8 file.
- **Do not use bare `$nl` derived from the source line** — after split the source element holds no terminator; derive nothing, hardcode the terminator.

## Modules / cpanm

- cpanm, cpan-outdated, gcc (MinGW-w64 13) ship with Strawberry. Installed modules: JSON::XS, Text::CSV_XS, File::Tail, Archive::Zip.
- Normal install: `cpanm --notest <Module...>` (needs network + firewall allowing perl.exe — SimpleWall/other WFP tools silently block NEW executables; `netsh advfirewall` may fail because the Defender Firewall service can be Disabled; ask the user to allow perl.exe in their firewall UI).
- Offline fallback (when perl.exe networking is blocked): download dist tarballs with python (`fastapi.metacpan.org/v1/module/<Module>` → `release` → `download_url`; `/v1/release/<Module>` 404s — module names use `::`, dist names use `-`), then `cpanm --notest ./<dist>.tar.gz` — XS modules compile with the bundled gcc.
- A stale HTTP 599 `Permission denied` on connect is the firewall signal, not a CPAN outage — curl/python working while perl fails proves it.

## Language facts for this user's tasks

- Perl beats Python ~1.5-2x on raw loops/strings but the LLM writes Python with far fewer error iterations; choose Perl for one-shot text/log filters, Python for anything maintained (token economics: C# ≈ 2x Python's code length, Perl ≈ 0.75x — but retries erase Perl's edge).
- `/usr/bin/perl` in git-bash reports `x86_64-cygwin` build — that is the Git-for-Windows perl, not a Cygwin install; don't try to update it via Cygwin setup.
