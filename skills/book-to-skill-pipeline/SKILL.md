---
name: book-to-skill-pipeline
description: "Use when converting a book (PDF/DOC/RTF) into a skill."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [books, distillation, skills, ocr, extraction, subagents, russian]
---

# Book → Skill Pipeline

Convert books (PDF/DOC/RTF, Russian-language included) into Hermes self-help skills: resolve .lnk shortcuts, extract text per format, OCR scanned pages, distill in parallel subagents, assemble SKILL.md + references.

User context for this machine: books arrive as `.lnk` shortcuts in `C:\Users\Administrator\Documents\!LAMA\books to skills\`; extracted texts go to `<same>\texts\`; finished skills get registered in Hermes AND the full folder copied to `C:\Users\Administrator\Documents\!LAMA\skills\<category>\<name>\` (verify with `diff -r`). Respond in Russian; when the user says "сделай то же самое" with a batch of books, process ALL of them (full books, not pilots) in waves — do not stop after one.

## Procedure

### 1. Resolve .lnk shortcuts
Parse the .lnk bytes in Python — scan for ANSI drive paths `[A-Za-z]:\...` and decode cp1251; prefer the candidate ending in a real extension (.pdf/.doc/.rtf/.djvu). Do NOT use PowerShell COM shortcuts for this: `.ps1` files written without BOM are read as ANSI by Windows PowerShell 5.1, so Cyrillic literals in the script corrupt the path (Test-Path silently False). Python byte-parsing sidesteps encoding entirely. Also: never inline PowerShell in `bash -c` — `$` is eaten by bash; always write a .ps1 file and run `powershell -ExecutionPolicy Bypass -File <path>`, redirecting output to a file when Cyrillic is involved.

### 2. Extract text by format
- `.pdf` → pymupdf (`import pymupdf`; the old `fitz` name warns). If a page's text layer is empty → it is a scan → step 3.
- `.doc` → `antiword` first. If antiword fails with "not a Word Document. It is probably a Rich Text Format file" — the file IS RTF: switch to Word COM.
- `.rtf` → Word COM. Do NOT write a custom RTF parser: real books contain fonttbl leaks and giant hex/OLE blobs that a hand parser turns into megabytes of garbage (a 1.2M-char book came out 7.6M). Word COM handles everything.
- Word COM: check `HKCU/HKLM \SOFTWARE\...\App Paths\WINWORD.EXE` first; open each doc `ReadOnly=True, AddToRecentFiles=False`, dump `doc.Content.Text`, `doc.Close(False)`, `word.Quit()` in `finally` with `Visible=False, DisplayAlerts=0`. Batch all files in one Word instance — startup dominates.
- When the same book exists as both .doc and .rtf: keep the one with the title page (.doc was the full 4th edition while .rtf began mid-book); check the first 300 chars of each before deciding.

### 3. OCR scanned pages (Russian) when paddlepaddle is absent
PaddleOCR 3.x needs the `paddlepaddle` engine (RuntimeError if missing) and `uv pip install` may be network-blocked. Working fallback: Windows built-in OCR via PowerShell WinRT (`Windows.Media.Ocr`):
- Render pages with pymupdf at dpi=200 to PNGs (`p001.png`...).
- Run `scripts/ocr_winrt_ru.ps1 <png_dir> <out.txt>` — it writes UTF-8 to a FILE.
- CRITICAL: force the engine with `TryCreateFromLanguage([Windows.Globalization.Language]::new('ru'))` — the default user-profile engine picks en-US and transliterates Cyrillic into Latin mojibake. Register the WinRT types (`[Windows.Globalization.Language,...]`) before use or you get "Unable to find type".
- Console stdout mangles Cyrillic regardless of engine — always write results via `[System.IO.File]::WriteAllText(..., [Text.Encoding]::UTF8)`, never print.
- Spot-check the first page before batch-running the rest.

### 4. Find book structure
Grep heading regexes (`^Глава N.`, `^Часть N.`, `^Тема N`) with a length cap (<60 chars) to skip TOC rows; Word COM exports keep TOC lines as real lines, so dedupe by checking both short-TOC-looking lines and later repeats. Record line ranges per chapter for splitting.

### 5. Parallel distillation (delegate_task)
- Split the text file into line ranges of ~800–1500 lines per subagent; one task per range. Subagents cannot read a 300K+ line book in one pass.
- Each task (in Russian): state the exact file path, the exact line range to read via read_file offset/limit, "НЕ выдумывай — только текст файла", the self-help framing (user applies the book to himself, not as a practitioner), output schema `{"markdown": "..."}`, and the required structure: «Знания-маркеры» / «Правила для себя» (MUST/SHOULD/MUST NOT) / «Самодиагностика», plus «Когда срочно к специалисту» for medical books. Demand "только дистиллят, без воды" with a line-count budget.
- Books >1M chars need 3+ parts; queue waves of ≤10 tasks and only dispatch the next wave after the current one returns (their results re-enter as one message per wave).

### 6. Merge subagent outputs
Summaries come back as JSON in `{"markdown": ...}` shape but sometimes wrapped in prose or ```json fences, and after `json.loads` the markdown still contains literal `\n` (backslash-n) from double escaping — replace `chr(92)+'n'` with real newlines. Use `scripts/merge_distillates.py` (tries whole-file loads → fenced block → first-`{`-to-last-`}`).

### 7. Assemble and register the skill
- Validator limits bite at create time: description ≤60 chars (one sentence, trigger first, ends with '.'; ~66 chars is rejected) and SKILL.md ≤100 000 chars. A full-book distillate (116K for a 176-page book) exceeds the cap — so SKILL.md holds the routing table (symptom → reference file), ~10 cross-cutting MUST/SHOULD principles, limitations, and `source:` path; the complete per-block distillate goes into `references/lectures-<range>.md`, each under 100K.
- `skill_manage create` with category (e.g. `self-help` for psychology books, name `self-help-<topic>`); then `mkdir -p` the skill's `references/` and `cp` the reference files in (create does not make the directory).
- Copy the whole skill folder to the user's `Documents\!LAMA\skills\` archive and verify `diff -r` returns IDENTICAL.
- Confirm with skill_view: `readiness_status: available`, all linked references listed.

## Pitfalls
- Custom RTF parsers on real books produce garbage (fonttbl + hex/OLE leaks). Word COM or nothing.
- PowerShell with Cyrillic: BOM-less .ps1 = ANSI interpretation = corrupted literals; Python byte work or ASCII-only .ps1 with args.
- WinRT OCR default engine transliterates Cyrillic to Latin — always construct the ru engine explicitly and verify page 1.
- antiword's "probably a Rich Text Format file" message is a truthful diagnostic: the .doc is really RTF.
- Subagent JSON: expect prose/fences around it and literal `\n` inside after json.loads; clean before writing files or the markdown has 700+ embedded `\n` artifacts.
- Antiword needs the native Windows path and decodes cp1251 unless given `-m UTF-8.txt`; git-bash mangles both — capture output to files, decode in Python.
- Session-scoped: the current session's skill index won't show a newly created skill until the next session — expected, not a bug.
