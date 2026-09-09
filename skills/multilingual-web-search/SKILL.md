---
name: multilingual-web-search
description: "Parallel web search in 5+ languages for wider coverage."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, search, multilingual]
    category: research
---

# Multilingual Web Search Skill

When performing web searches, issue several parallel queries in different
languages simultaneously to get broader, more diverse results. Never rely
on a single-language query alone.

## When to Use

Any time `web_search` is called for factual, statistical, or
comparative information.

## How to Run

1. Formulate the original query in the language of the user's question.
2. Translate the query into **at least 4-5** of these languages:
   English, Chinese (simplified), Spanish, German, French, Japanese,
   Russian, Arabic, Portuguese.
3. Issue ALL queries in **one batch** of parallel `web_search` calls.
4. Parse results from all languages; non-English results often surface
   different sources and perspectives.
5. Cross-reference and synthesise the best data from all language pools.

## Quick Reference

| Language | Typical query prefix / phrasing |
|---|---|
| English | `"top 10" OR statistics` |
| Chinese | Use `site:zh.` or Chinese keywords |
| Spanish | `"los 10 principales" OR estadísticas` |
| German | `"Top 10" OR Statistik` |
| French | `"top 10" OR statistiques` |
| Japanese | `トップ10 OR 統計` |
| Russian | `"топ 10" OR статистика` |

## Pitfalls

- Do NOT batch 10+ queries in one turn if the results are
  interdependent — batch only independent lookups.
- Non-English queries may return sources the model can't read; use
  `web_extract` on promising URLs regardless of language.
- Google-dominated queries in English may miss content that is only
  indexed in the local language's search ecosystem.