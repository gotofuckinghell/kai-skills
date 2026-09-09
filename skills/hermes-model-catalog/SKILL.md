---
name: hermes-model-catalog
description: "Fix Hermes model picker. Understand curated vs live lists."
version: 1.0.0
author: Hermes Agent (auto-curated)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, model-picker, openrouter, catalog, configuration, curated-models]
---

# Hermes Model Catalog

Hermes doesn't show every model from a provider's live API — it uses **curated lists** to keep the picker focused. This skill covers how to understand, extend, and debug those lists.

## How the Model Picker Works

### OpenRouter

1. Fetches the **remote curated manifest** from `hermes-agent.nousresearch.com/docs/api/model-catalog.json`
2. Falls back to **hardcoded `OPENROUTER_MODELS`** in `hermes_cli/models.py`
3. Fetches live **`/v1/models`** API for pricing/tool-support enrichment
4. Iterates **only over the curated list (preferred_ids)** — live-only models are **silently dropped**

Key filtering in `fetch_openrouter_models()`:
- Models must advertise **tool support** (`"tools" in supported_parameters`)
- `pricing: -1` (variable/unknown) — passes through only if in the curated list

### Other Providers

- **Nous Portal**: similar curated list in `model_catalog.json` + `_PROVIDER_MODELS["nous"]`
- **Vercel AI Gateway**: `VERCEL_AI_GATEWAY_MODELS` in `models.py`
- **Custom providers**: their own `/v1/models` endpoint

## How to Add a Missing OpenRouter Model

Hermes only shows models in the **curated list** (`model-catalog.json` or `OPENROUTER_MODELS`). Live-API-only models are silently dropped.

### Step 1 — Add to `OPENROUTER_MODELS` fallback list

In `hermes_cli/models.py`, find the `# OpenRouter routers` section (~line 133) and add entries:

```python
# OpenRouter routers
("openrouter/pareto-code", "auto-routes to cheapest coder meeting openrouter.min_coding_score"),
("openrouter/auto",         ""),
("openrouter/free",         "free"),
```

### Step 2 — Inject router models into the curated list

In `fetch_openrouter_models()`, after the main loop builds `curated`, inject router models. This catches models that exist in the live API but are absent from the curated manifest:

```python
curated_ids = {mid for mid, _ in curated}

_ROUTER_MODEL_IDS = (
    "openrouter/auto",
    "openrouter/free",
    "openrouter/auto-beta",
    "openrouter/fusion",
)

router_entries: list[tuple[str, str]] = []
for router_id in _ROUTER_MODEL_IDS:
    if router_id in curated_ids:
        continue
    live_item = live_by_id.get(router_id)
    if live_item is None:
        continue
    if not _openrouter_model_supports_tools(live_item):
        continue
    desc = "free" if _openrouter_model_is_free(live_item.get("pricing")) else ""
    router_entries.append((router_id, desc))

if router_entries:
    # Insert right after the first "recommended" entry (~position 2)
    # so they appear at the top of the picker without scrolling.
    insert_at = 1 if len(curated) > 1 else len(curated)
    for i, entry in enumerate(router_entries):
        curated.insert(insert_at + i, entry)
```

### Step 3 — Clear caches and deploy

```bash
# Clear Python bytecode cache (forces recompile)
del "%HERMES_HOME%\hermes-agent\hermes_cli\__pycache__\models.cpython-311.pyc"

# Clear disk model catalog cache
del "%LOCALAPPDATA%\hermes\cache\model_catalog.json"
del "%LOCALAPPDATA%\hermes\cache\openrouter_model_metadata.json"

# Refresh picker (re-fetches live catalog)
hermes model --refresh
```

### Common pitfalls discovered

| Pitfall | Symptom | Fix |
|---|---|---|
| Router model at end of list | User can't scroll to see it | Insert at position 1 (after first recommended) |
| Searching by hardcoded description | `curated.index(("openrouter/pareto-code", "..."))` fails if live API strips description | Use `next(i for i,(m,_) in enumerate(curated) if m == "openrouter/...")` |
| `pareto-code` filtered out | `pareto-code` not in picker even though in curated list | Live API returns `tools: False` for `pareto-code` — filter runs AFTER adding from curated list |
| `fusion` filtered out | `openrouter/fusion` silently absent | Fails `_openrouter_model_supports_tools()` — expected, it has no tools |
| Cache not cleared | Old model list still shows | Delete `model_catalog.json` AND `.pyc` file |

### Live API quick check

```python
import requests, json
r = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
items = {m["id"]: m for m in r.json()["data"]}
for mid in ["openrouter/auto", "openrouter/free", "openrouter/fusion"]:
    item = items.get(mid, {})
    print(f"{mid}: tools={('tools' in (item.get('supported_parameters') or []))}, price={item.get('pricing')}")
```

## Key Files

- `hermes_cli/models.py` — `OPENROUTER_MODELS` (~line 105), `fetch_openrouter_models()` (~line 2016), `CANONICAL_PROVIDERS` (~line 1320), `_PROVIDER_MODELS` (~line 267)
- `hermes_cli/auth.py` — `PROVIDER_REGISTRY` (~line 249) — required for new API-key providers
- `hermes_cli/main.py` — `select_provider_and_model()` dispatch set (~line 4192) — required for new API-key providers
- `hermes_cli/model_catalog.py` — remote manifest fetcher + disk cache
- `~/.hermes/cache/model_catalog.json` — disk cache
- `~/.hermes/cache/openrouter_model_metadata.json` — reasoning caps cache

## Related

- `references/adding-an-api-key-provider.md` — three-file pattern for new API-key providers (Groq worked example)
- `references/openrouter-router-injection.md` — injecting `openrouter/auto` / `openrouter/free` into the curated list
- `references/local-ocr-engines.md` — PaddleOCR 3.x vs RapidOCR: which engine for which language, and the 3.x API changes that break old constructors

## Adding a brand-new API-key provider (e.g. Groq)

When a provider is missing from the picker entirely — not just a missing model — three coordinated patches are required. See `references/adding-an-api-key-provider.md` for the full pattern (Groq worked example: `auth.py` `PROVIDER_REGISTRY` + `models.py` `CANONICAL_PROVIDERS` + `models.py` `_PROVIDER_MODELS` + `main.py` dispatch set).