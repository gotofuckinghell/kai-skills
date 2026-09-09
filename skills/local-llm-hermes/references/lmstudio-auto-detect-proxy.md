# LM Studio Auto-Detect Proxy

When LM Studio loads one model at a time, hardcoding a model name in Hermes's alias breaks every time the user switches models in LM Studio. The proxy solves this: Hermes sends `model: __auto__`, the proxy probes all LM Studio models in parallel, finds the loaded one (responds in <1s), rewrites the model name, and forwards to LM Studio.

## Setup

1. Place `scripts/lmstudio-proxy.py` (see below)
2. Start it: `python ~/.hermes/scripts/lmstudio-proxy.py` (listens on :1235)
3. Configure Hermes alias:

```bash
hermes config set model_aliases.local.model "__auto__"
hermes config set model_aliases.local.provider custom
hermes config set model_aliases.local.base_url "http://localhost:1235/v1"
hermes config set model_aliases.local.api_key lm-studio
hermes config set model_aliases.local.context_length 131072
```

## How it works

- `GET /v1/models` → forwarded to LM Studio (:1234), returns full model list
- `POST /v1/chat/completions` with `model: __auto__` → parallel probe of all models; loaded model responds instantly; proxy rewrites `model` field, forwards, returns
- Cache TTL: 30 seconds — avoids re-probing on every request
- Parallel probe via `ThreadPoolExecutor` — total detection time <3s

## Context size note

Hermes requires 64K minimum context. LM Studio often reports half the true context (e.g. 32K for Gemma 3 27B which actually has 128K). Always set `context_length` in the alias to the model's true maximum: 131072 for most modern models, 32768 for older ones.

## LM Studio hosting all downloaded models

LM Studio's `/v1/models` endpoint returns ALL downloaded models, not just the loaded one. The proxy detects the loaded model by measuring response time — loaded models respond in <1s, unloaded ones either fail or take 10-30s to load.