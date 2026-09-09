# OpenRouter Router Model Injection

`openrouter/auto`, `openrouter/free`, `openrouter/auto-beta`, and `openrouter/fusion` are **pseudo-models** — they don't represent a single LLM but routing logic on OpenRouter's side. The curated manifest (`model-catalog.json`) doesn't list them, so they're invisible in the Hermes picker.

## Detection Signs

- `openrouter/free` exists in live `/v1/models` API (pricing: `{prompt: "0", completion: "0"}`) but doesn't appear in picker
- `openrouter/auto` exists (pricing: `-1` = variable) but doesn't appear
- Running `fetch_openrouter_models()` returns only the curated-count models; router models are absent
- `openrouter/fusion` is in live API but has `supported_parameters: []` (no tools) → filtered out by `_openrouter_model_supports_tools`

## Fix: Two-Change Pattern

### 1. Add to OPENROUTER_MODELS (`hermes_cli/models.py`)

Under the `# OpenRouter routers` comment:

```python
("openrouter/auto",                        ""),
("openrouter/free",                        "free"),
```

This ensures the fallback path (when remote catalog is unreachable) also carries them.

### 2. Inject in fetch_openrouter_models()

After the main curated loop, inject from the live API:

```python
# After curated list loop
curated_ids = {mid for mid, _ in curated}

# Router/utility model IDs to inject from live catalog
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
    # Insert near top so they're visible without scrolling
    insert_at = 1 if len(curated) > 1 else len(curated)
    for i, entry in enumerate(router_entries):
        curated.insert(insert_at + i, entry)
```

### 3. Position matters

Don't append — they end up at #47-49 out of 49 and users never scroll to them. Insert at position 1 (right after the recommended entry).

## Cache Clearing

```bash
# Delete compiled bytecode
rm hermes_cli/__pycache__/models.cpython-*.pyc
# Clear picker disk cache
hermes model --refresh
```

## Verification

```python
from hermes_cli.models import fetch_openrouter_models
models = fetch_openrouter_models(timeout=15, force_refresh=True)
for mid, desc in models:
    if mid.startswith("openrouter/auto") or mid.startswith("openrouter/free"):
        print(f"  {mid} -> {desc!r}")
```

Expected:
- `openrouter/auto -> ''` (variable pricing, no free tag)
- `openrouter/free -> 'free'` (zero pricing, has free tag)
- `openrouter/auto-beta -> ''`
- `openrouter/fusion` → absent (filtered by tools check)
