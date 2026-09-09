---
name: ai-platform-migration
description: Import chat exports, extract user profile, and seed memory.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [migration, import, data-portability, memory-seeding, user-profiling]
    category: productivity
    related_skills: [session-librarian]
---

# AI Platform Migration Skill

Import exported chat history from other AI platforms (DeepSeek, ChatGPT, Claude) and
seed Hermes persistent memory with an extracted user profile: demographics,
interests, technical skills, languages, recurring topics, and interaction style.

## When to Use

- User mentions an exported chat history file from another AI platform.
- User wants Hermes to "learn from" or "absorb" their past AI conversations.
- Setting up a new Hermes user profile and there's an existing export available.

## Prerequisites

- The exported file in the user's filesystem (typically `~/Downloads/`).
- `python` (stdlib only — `zipfile`, `json`, `re`, `collections.Counter`).

## How to Run

1. Locate the file: `search_files` in `~/Downloads/` for `*deepseek*`, `*chatgpt*`, `*claude*`.
2. Unpack if ZIP, inspect structure, sample a few conversations.
3. Classify topics by title and first-user-message keywords.
4. Detect languages per user message via character-class regex.
5. Extract personal facts: location, age, occupation, games, tech stack.
6. Save 3–6 compact memory entries via `memory` tool (target: `user`).
7. Present a summary report.

## Quick Reference

| Platform | Export format |
|---|---|
| DeepSeek | ZIP: `conversations.json` (mapping-tree), `user.json` |
| ChatGPT | ZIP: `conversations.json` (array of `{title, mapping}`) |
| Claude | JSON: conversations array with name and chat_messages |

DeepSeek message tree: each mapping entry has `{id, parent, children, message}`.
Messages carry `{model, inserted_at, fragments: [{type: "REQUEST"|"RESPONSE", content}]}`.
The `root` node has `message: null` — skip it.
Full format reference: `references/deepseek-export-format.md`.

## Procedure

### Phase 1 — Discovery and sampling

```python
import zipfile, json
z = zipfile.ZipFile(path)
convs = json.loads(z.read('conversations.json'))
print(f'Conversations: {len(convs)}')
```

Sample the first conversation to confirm the schema. Run as `execute_code`.

### Phase 2 — Topic classification

Group by title keyword matching. Use a `defaultdict(list)` with keyword sets per
expected topic. Tailor keywords per user — start broad and refine.

Pitfall: DeepSeek titles are auto-generated, often in Russian, and may not contain
the obvious English keyword. Check both Russian and English stems.

### Phase 3 — Language detection

Use character-class regex, not `langdetect` (no pip install needed):

```python
def detect_lang(text):
    has_ru = bool(re.search(r'[а-яёА-ЯЁ]', text))
    has_cs = bool(re.search(r'[ěščřžýáíéúůďťňó]', text))
    has_uk = bool(re.search(r'[іїєґ]', text))
    langs = []
    if has_ru: langs.append('ru')
    if has_cs: langs.append('cs')
    if has_uk: langs.append('uk')
    if not langs and re.search(r'[a-zA-Z]{3}', text): langs.append('en')
    return '+'.join(langs) if langs else 'other'
```

### Phase 4 — Personal fact extraction

Use `re.search` across all user messages for: location, age, occupation, games,
languages, tech stack.

### Phase 5 — Memory seeding

Use `memory` with `operations` array — compact, 3–6 entries. Remove stale entries
in the same batch if nearing the 1375-char budget.

### Phase 6 — Report

Summary table: topic groups with counts, language distribution, extracted profile,
period covered.

## Pitfalls

- **DeepSeek `mapping` is a flat dict, not a tree.** The `parent`/`children` fields form
  the tree — iterate all keys. The `root` node has `message: null`.
- **Content can be a string, object, or empty dict.** Always check `isinstance(content, str)`.
- **Titles are unreliable for classification.** Fall back to first user message content.
- **Language detection is crude.** Czech chars disambiguate cs from ru, but mixed
  messages are common for bilingual users.
- **Memory budget is tight (1375 chars).** Batch removes with adds in one call.

## Verification

- `memory(target='user')` returns the seeded entries.
- Ask the user: "Does this profile look right?"