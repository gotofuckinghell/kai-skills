# Adding a New API-Key Provider to Hermes

When a provider (Groq, Fireworks, Cohere, etc.) is missing from `hermes model`'s picker — even though it's OpenAI-compatible and would otherwise work — Hermes needs three coordinated patches before the picker shows it. The provider is then runnable through the standard `hermes model` flow (which calls `_model_flow_api_key_provider`), the credential pool, and `hermes auth add <id>`.

## The Three Files to Patch

### 1. `hermes_cli/auth.py` — add `ProviderConfig` to `PROVIDER_REGISTRY`

`PROVIDER_REGISTRY` is the single source of truth for known API-key providers. Without an entry here, the model flow short-circuits and never reaches `_prompt_api_key`.

```python
# In PROVIDER_REGISTRY dict, add:
"groq": ProviderConfig(
    id="groq",
    name="Groq",
    auth_type="api_key",
    inference_base_url="https://api.groq.com/openai/v1",
    api_key_env_vars=("GROQ_API_KEY",),
    base_url_env_var="GROQ_BASE_URL",
),
```

Notes:
- `api_key_env_vars` is a tuple — first entry is the canonical env var; later entries are fallback aliases.
- `base_url_env_var` is the env var users set to override the default (leave `""` if no override is sensible).
- `inference_base_url` is the OpenAI-compatible chat completions endpoint, **not** the root marketing URL. Groq: `https://api.groq.com/openai/v1`, not `https://api.groq.com/v1`.

### 2. `hermes_cli/models.py` — add to both `CANONICAL_PROVIDERS` and `_PROVIDER_MODELS`

Two separate additions:

```python
# In CANONICAL_PROVIDERS list (~line 1320) — drives the picker UI:
ProviderEntry("groq", "Groq", "Groq (Fast inference: Llama 3.3, Mixtral, Gemma)"),

# In _PROVIDER_MODELS dict (~line 267) — drives /v1/models probing and offline fallback:
"groq": [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "whisper-large-v3-turbo",
],
```

Skip either side and the provider shows in the picker but can't enumerate models, OR the provider works but doesn't show in the picker. Both are required.

### 3. `hermes_cli/main.py` — add to the `_model_flow_api_key_provider` dispatch set

Inside `select_provider_and_model()`, there is an `elif` that lists every provider that should flow into `_model_flow_api_key_provider`. New API-key providers must be added there explicitly — the catch-all `_is_profile_api_key_provider()` only fires for plugin-declared providers, not in-repo edits.

```python
elif selected_provider in {
    "openai-api",
    "gemini",
    # ... existing entries ...
    "lmstudio",
    "groq",   # ← add here
} or _is_profile_api_key_provider(selected_provider):
    _model_flow_api_key_provider(config, selected_provider, current_model)
```

## Verify the Patch

```bash
# Syntax sanity:
cd C:/Users/Administrator/AppData/Local/hermes/hermes-agent
python -c "from hermes_cli.auth import PROVIDER_REGISTRY; print('groq' in PROVIDER_REGISTRY)"
# → True

python -c "from hermes_cli.models import CANONICAL_PROVIDERS; print(any(p.slug == 'groq' for p in CANONICAL_PROVIDERS))"
# → True

# Functional check — provider should appear in the picker, and picking it should
# trigger GROQ_API_KEY prompt:
hermes model
# Look for "Groq (Fast inference: ...)" in the list, choose it.
# Expected: "No Groq API key configured. GROQ_API_KEY (or Enter to cancel):"
```

## Clear Caches

```bash
# Python bytecode (forces reimport):
del "%LOCALAPPDATA%\hermes\hermes-agent\hermes_cli\__pycache__\auth.cpython-311.pyc"
del "%LOCALAPPDATA%\hermes\hermes-agent\hermes_cli\__pycache__\models.cpython-311.pyc"
del "%LOCALAPPDATA%\hermes\hermes-agent\hermes_cli\__pycache__\main.cpython-311.pyc"

# Disk model catalog:
del "%LOCALAPPDATA%\hermes\cache\model_catalog.json"
```

## After the Patch — Wiring the Credential

There are three ways to provide the key (any one is enough; credential pool rotates across all):

1. `hermes auth add groq` → interactive, stored in `auth.json`.
2. `hermes config set groq_api_key <key>` (writes to `.env`).
3. Set the env var directly: `export GROQ_API_KEY=<key>` (or Windows `set`).

`hermes doctor` will report which keys it can see and which it can't.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Skip `auth.py` edit | `hermes model` shows provider but selection immediately returns | `_model_flow_api_key_provider` is never called for unknown providers in the in-repo dispatch set. The catch-all only fires for plugin-declared profiles. |
| Skip `models.py` `CANONICAL_PROVIDERS` | Picker works, but `/provider groq` from chat errors | Provider isn't enumerable for the dispatcher that drives `/provider <name>` and CLI `--provider` flag validation. |
| Skip `models.py` `_PROVIDER_MODELS` | Picker shows provider, but selecting it offers no model | Model enumeration is empty, so the flow can't prompt for one. |
| Use wrong base URL (e.g. `https://api.groq.com/v1` instead of `/openai/v1`) | Provider selected, key saved, every request 404s on `/chat/completions` | Verify the OpenAI-compatible path. Groq's is `/openai/v1`; Mistral's is `/v1`; OpenAI's is `/v1`. |
| Two near-identical entries (e.g. adding both `groq` and `groq-cloud`) | Provider picker shows duplicates | The provider ID is the slug. Use one canonical ID and add aliases via `model_switch.py` if you need name variations. |
| Edit `config.yaml` directly to add the provider | Indent error corrupts the live gateway | Use `hermes config set` exclusively; the runtime reloads on the next call. |

## Why Three Files

Hermes is provider-agnostic and uses **three coordinated registries** so a provider can be (a) discovered in the picker, (b) authenticated, and (c) dispatched into the right flow. No single file holds all three. Skipping any of them produces a half-working provider that the user can't get past.

| Registry | What it owns | File |
|---|---|---|
| Provider identity & auth | `auth_type`, `api_key_env_vars`, `inference_base_url` | `hermes_cli/auth.py` → `PROVIDER_REGISTRY` |
| Picker UI & model list | display label, description, curated model IDs | `hermes_cli/models.py` → `CANONICAL_PROVIDERS` + `_PROVIDER_MODELS` |
| Interactive flow dispatch | which `_model_flow_*` to call for selection | `hermes_cli/main.py` → `select_provider_and_model()` dispatch set |

## Related

- `references/openrouter-router-injection.md` — for adding an OpenRouter model to the curated list (different surface area, no auth.py or main.py edits needed).
- Top-level skill: `hermes-model-catalog` SKILL.md (curated vs live lists overview).
