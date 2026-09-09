# Model Alias Forms

Two DIFFERENT config keys, easy to confuse. This session hit this exact pitfall multiple times.

## model_aliases (TOP-LEVEL key) — Full override

```yaml
model_aliases:
  local:
    provider: custom
    model: "qwen/qwen3.5-9b"
    base_url: "http://localhost:1234/v1"
    api_key: lm-studio
    context_length: 131072
```

CLI:
```bash
hermes config set model_aliases.local.provider custom
hermes config set model_aliases.local.model "qwen/qwen3.5-9b"
hermes config set model_aliases.local.base_url "http://localhost:1234/v1"
hermes config set model_aliases.local.api_key lm-studio
hermes config set model_aliases.local.context_length 131072
```

Supports: `provider`, `model`, `base_url`, `api_key`, `context_length`, and other provider-level overrides.
REQUIRED for local inference servers because they need a custom base_url.

## model.aliases (NESTED under model) — Shortcut only

```yaml
model:
  aliases:
    local: "custom/qwen3:14b"
```

CLI:
```bash
hermes config set model.aliases.local "custom/qwen3:14b"
```

Only maps a shortcut name to a model string within the current provider. CANNOT set base_url, api_key, or context_length.

## Symptom of using the wrong one

`/model local` → `✗ Model 'local' was not found in this provider's model listing.`

Hermes sends "local" as the model name to OpenRouter instead of resolving it as a custom provider alias.

## LM Studio auto-detect with __auto__

For LM Studio specifically, avoid hardcoding model names entirely. Use the auto-detect proxy (see `local-llm-hermes` skill → `scripts/lmstudio-proxy.py`):

```bash
hermes config set model_aliases.local.model "__auto__"
hermes config set model_aliases.local.base_url "http://localhost:1235/v1"
```