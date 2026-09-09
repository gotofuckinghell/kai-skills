# Lemonade Custom Models — Full Reference

Excerpted from Lemonade Server docs (https://lemonade-server.ai/docs/guide/configuration/custom-models/). Covers every supported way to add a custom model.

## Quick CLI workflows

### Pull from Hugging Face (default source)

```bash
lemonade pull org/repo                    # interactive quant picker
lemonade pull org/repo:Q4_K_M             # specific quant
lemonade pull https://huggingface.co/unsloth/Qwen3-8B-GGUF
```

### Pull from ModelScope

```bash
lemonade pull --source modelscope org/repo
lemonade pull --source modelscope org/repo:Q4_K_M
```

### Register with explicit flags

```bash
lemonade pull user.NAME \
    --source SOURCE \
    --checkpoint TYPE CHECKPOINT \
    --recipe RECIPE \
    --label LABEL ...
```

Examples:

```bash
# Single GGUF
lemonade pull user.Phi-4-Mini-GGUF \
    --checkpoint main unsloth/Phi-4-mini-instruct-GGUF:Q4_K_M \
    --recipe llamacpp

# Vision model (main + mmproj)
lemonade pull user.Gemma-3-4b \
    --checkpoint main ggml-org/gemma-3-4b-it-GGUF:Q4_K_M \
    --checkpoint mmproj ggml-org/gemma-3-4b-it-GGUF:mmproj-model-f16.gguf \
    --recipe llamacpp

# With labels
lemonade pull user.MyCodingModel \
    --checkpoint main org/model:Q4_0 \
    --recipe llamacpp \
    --label coding \
    --label tool-calling
```

## Registration flags

| Flag | Description |
|------|-------------|
| `--source SOURCE` | `huggingface` or `modelscope` |
| `--checkpoint TYPE CHECKPOINT` | Repeat for multi-file models (main + mmproj, main + vae) |
| `--recipe RECIPE` | `llamacpp`, `whispercpp`, `moonshine`, `kokoro`, `sd-cpp`, `flm`, `ryzenai-llm`, `vllm`, `thenoise`, `thinksound`, `acestep`, `onnxruntime`, `trellis`, `openmoss`, `collection.omni` |
| `--label LABEL` | Repeatable: `chat`, `coding`, `dflash`, `embeddings`, `hot`, `mtp`, `reasoning`, `reranking`, `tool-calling`, `vision` |

## Using local GGUF files (no download)

Drop `.gguf` files into `%USERPROFILE%\.config\lemonade\extra-models\` (Windows) or `~/.config/lemonade/extra-models/` (Linux/macOS). They appear as `extra.<filename>` immediately — no config editing needed.

## Model naming and precedence

Three sources, resolved in order: **registered > imported > built-in**.

| Canonical ID | Source |
|-------------|--------|
| `user.NAME` | Registered via `lemonade pull` (in `user_models.json`) |
| `extra.NAME` | GGUF dropped in `--extra-models-dir` |
| `builtin.NAME` | Shipped with Lemonade (`server_models.json`) |

The bare name `NAME` resolves to the highest-precedence source. Shadowed sources are addressable by their canonical prefix.

## Checkpoint formats

- **GGUF exact filename**: `org/repo:filename.gguf`
- **GGUF quant shorthand**: `org/repo:Q4_K_M` — server searches repo for matching `.gguf`
- **ONNX models**: `org/repo`
- **Safetensor models**: `org/repo:filename.safetensors`

## Multi-file models (checkpoints object)

For Whisper with NPU cache, Flux with VAE/text encoder:

```json
{
    "My-Whisper-Model": {
        "checkpoints": {
            "main": "ggerganov/whisper.cpp:ggml-tiny.bin",
            "npu_cache": "amd/whisper-tiny-onnx-npu:ggml-tiny-encoder-vitisai.rai"
        },
        "recipe": "whispercpp",
        "size": 0.075
    }
}
```

Supported keys: `main`, `npu_cache` (whispercpp), `text_encoder` (sd-cpp), `vae` (sd-cpp).

## Recipe options (per-model runtime settings)

File: `recipe_options.json` in Lemonade config dir. Keyed by canonical model ID.

```json
{
    "user.MyCustomModel": {
        "ctx_size": 16384,
        "llamacpp_backend": "vulkan",
        "llamacpp_args": ""
    }
}
```

## Register via API

```bash
curl -X POST http://localhost:13305/v1/pull \
    -H "Content-Type: application/json" \
    -d '{
        "model_name": "user.MyModel",
        "recipe": "llamacpp",
        "checkpoint": "org/repo:Q4_K_M"
    }'
```

## Config file locations (Windows)

| File | Path |
|------|------|
| `user_models.json` | `%USERPROFILE%\.config\lemonade\` |
| `recipe_options.json` | `%USERPROFILE%\.config\lemonade\` |
| Extra models dir | `%USERPROFILE%\.config\lemonade\extra-models\` |