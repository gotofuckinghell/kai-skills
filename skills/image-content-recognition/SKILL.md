---
name: image-content-recognition
description: "Recognize image content using vision-language models (Florence-2, MobileNetV2) with GPU acceleration."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, windows, macos]
metadata:
  hermes:
    tags: [image-recognition, vision, florence-2, mobilenetv2, directml, gpu, intel-arc, amd-radeon, document-analysis]
    related_skills: [ocr-and-documents, gpu-ocr-pipeline]
---

# Image Content Recognition (Beyond OCR)

Recognize what images *contain* — not just extract text. Understand scenes, classify diagrams, generate captions. Two paths: MobileNetV2 (fast general) and Florence-2 (deep semantic).

## When to Use

- Identifying the content/scenario of a scanned page or document image
- Technical diagram classification (schematics, PCBs, component layouts)
- Scene/object recognition in scanned documents
- Generating captions that describe what's in an image
- Understanding what a picture shows (not just OCR)

## Stack (Non-NVIDIA Hardware)

### Recommended: Florence-2 via HuggingFace Transformers (WORKING 2026-09-01)

**Florence-2 via transformers is the primary working path.** The ONNX models from `onnx-community/Florence-2-base-ft/` have graph fusion incompatibility with onnxruntime 1.26+ — they fail to load with `InsertedPrecisionFreeCast_` errors. Use HuggingFace transformers instead.

**Install (exact versions required)**:
```bash
uv pip install torch==2.4.1 torchvision==0.19.1 einops
uv pip install "transformers>=4.40,<5.0"
```
- `torch>=2.5` → torchvision incompatible → import error
- `transformers>=5.0` → missing `AutoProcessor` module → import error
- `torch<2.4` → likely works but untested
- `torch==2.8.0` → torchvision incompatibility → `torchvision::nms does not exist`

**Model download**: Automatically downloaded by transformers from `microsoft/Florence-2-base`. Cache: `C:/Users/Administrator/AppData/Local/hermes/cache/hf/`

**Full model saved to**: `C:/Users/Administrator/Documents/!LAMA/scripts/florence2_models/full/`

### Working ONNX Models (Limited Use)

| Component | Size | Status |
|-----------|------|--------|
| `mobilenetv2-10.onnx` | 14MB | ✅ Works |
| `embed_tokens_q4f16.onnx` | 79MB | ✅ Loads (standalone) |
| `vision_encoder_q4f16.onnx` | 62MB | ❌ Graph fusion error |
| `encoder_model_q4f16.onnx` | 26MB | ❌ Graph fusion error |
| `decoder_model_q4f16.onnx` | 56MB | ❌ Graph fusion error |
| `decoder_model_merged_q4.onnx` | 64MB | ❌ Graph fusion error |

**ONNX location**: `C:/Users/Administrator/Documents/!LAMA/scripts/florence2_models/onnx/`

**Do NOT install**: plain `onnxruntime` (CPU/Azure only). Use `onnxruntime-directml`.

## Florence-2 via Transformers (PRIMARY METHOD)

```python
import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
import warnings
warnings.filterwarnings("ignore")

from transformers import AutoModelForCausalLM, AutoProcessor
import torch
from PIL import Image

# Load model (once, reuse session)
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True,
    cache_dir="C:/Users/Administrator/AppData/Local/hermes/cache/hf",
    low_cpu_mem_usage=True,
    attn_implementation="eager"  # REQUIRED — SDPA causes AttributeError
)
processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True,
    cache_dir="C:/Users/Administrator/AppData/Local/hermes/cache/hf"
)

# Describe image
img = Image.open("image.png").convert("RGB")
inputs = processor(text="<CAPTION>", images=img, return_tensors="pt")

# Use generate() with use_cache=False — bypasses past_key_values bug
generated_ids = model.generate(
    input_ids=inputs["input_ids"],
    pixel_values=inputs["pixel_values"],
    max_new_tokens=50,
    do_sample=False,
    num_beams=1,
    use_cache=False,  # Required — bypasses past_key_values=None bug
    return_dict_in_generate=True
)

raw_text = processor.tokenizer.batch_decode(
    generated_ids.sequences, skip_special_tokens=False
)[0]

# Post-process with Florence-2's own method
parsed = processor.post_process_generation(
    raw_text,
    task="<CAPTION>",
    image_size=(img.width, img.height)
)
caption = parsed.get("<CAPTION>", raw_text)
print(caption)
```

### Task Prompts for Florence-2

| Task | Prompt | Output |
|------|--------|--------|
| Simple caption | `<CAPTION>` | Short description |
| Detailed caption | `<DETAILED_CAPTION>` | Full description |
| More detail | `<MORE_DETAILED_CAPTION>` | Extended description |
| Object detection | `<OD>` | Bounding boxes |
| OCR | `<OCR>` | All text in image |
| Phrase detection | `<CAPTION> <OD>` | Both caption + boxes |

### Florence-2 Architecture (Known Structure)

```
Florence2ForConditionalGeneration
├── vision_tower (DaViT) — image → patch embeddings
├── language_model (Florence2LanguageForConditionalGeneration) — text decoder
└── NO separate encoder attribute
```

- `model.vision_tower` → DaViT vision encoder
- `model.language_model` → decoder (accepts `input_ids` + `inputs_embeds`)
- `model.get_input_embeddings()` → text embedding layer
- **DaViT forward is complex** — requires `forward_features()` → `norms()` internal chain; ONNX export fails

## MobileNetV2 via ONNX (Fallback / Fast)

```python
import onnxruntime as ort
import numpy as np
from PIL import Image

providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
session = ort.InferenceSession('mobilenetv2-10.onnx', providers=providers)

# Preprocess
img = Image.open('page.png').convert('RGB').resize((224, 224))
arr = np.array(img, dtype=np.float32) / 255.0  # EXPLICIT dtype required
mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
arr = (arr - mean) / std
arr = np.transpose(arr, (2, 0, 1))  # HWC → CHW
arr = np.expand_dims(arr, axis=0)

# Inference
outputs = session.run([session.get_outputs()[0].name], {session.get_inputs()[0].name: arr})
predictions = outputs[0].squeeze()

# Softmax (raw logits are NOT probabilities)
exp_x = np.exp(predictions - np.max(predictions))
predictions = exp_x / np.sum(exp_x)

# Top-5
for idx in np.argsort(predictions)[-5:][::-1]:
    print(f"{idx}: {predictions[idx]:.2%}")
```

## Preprocessing Checklist (Critical)

All ONNX vision models require:
1. **Resize** to model input (MobileNetV2 = 224x224, Florence-2 = 384x384)
2. **RGB conversion**
3. **ImageNet normalization**: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
4. **Cast to float32 explicitly**: `np.array(img, dtype=np.float32)` — NOT `.astype()`. Without explicit dtype, numpy may produce float64 → ONNX `InvalidArgument: Unexpected input data type`
5. **CHW format**: transpose HWC → CHW, then batch dimension

## Known Issues & Fixes

### transformers import fails with `Could not import module 'AutoProcessor'`
- Cause: transformers 5.16.1 is broken, OR torch torchvision version mismatch
- Fix: `uv pip install torch==2.4.1 torchvision==0.19.1 "transformers>=4.40,<5.0"`

### `torchvision::nms does not exist`
- Cause: torch 2.8.0 + torchvision 0.19.1 mismatch
- Fix: `uv pip install torch==2.4.1 torchvision==0.19.1`

### Florence-2 `model.generate()` raises `AttributeError: 'NoneType' object has no attribute 'shape'`
- Cause: bug in transformers 4.57.6 with `past_key_values=None`
- Fix: pass `use_cache=False` to `model.generate()` — this is the simplest and most reliable fix (discovered 2026-09-01). The manual autoregressive loop also works but is more complex.

### `early_stopping` Flag Silently Ignored by Florence-2
- Observed (2026-09-01): passing `early_stopping=True` to `model.generate()` produces warning: "The following generation flags are not valid and may be ignored: ['early_stopping']". The flag is silently dropped — do not rely on it.

### Florence-2 raises `AttributeError: ... '_supports_sdpa'`
- Cause: SDPA attention incompatible with this model
- Fix: always pass `attn_implementation="eager"` to `from_pretrained()`

### Florence-2 processor: `AssertionError: Task token <CAPTION> should be the only token`
- Cause: used `processor.tokenizer.bos_token + "<CAPTION>"` — BOS already in tokenizer
- Fix: use only `"<CAPTION>"` as the text prompt

### ONNX model fails to load: `InsertedPrecisionFreeCast_`
- Cause: graph fusion incompatibility between exported ONNX and onnxruntime 1.26+
- Fix: use HuggingFace transformers instead (primary method)

### ONNX model fails: `'DaViT' object has no attribute 'norms'`
- Cause: DaViT forward() calls internal norms that aren't accessible for tracing
- Fix: use HuggingFace transformers (DaViT is complex custom module)

## Video Frame Analysis Workflow

For video content understanding, extract frames with ffmpeg then analyze each frame:

```bash
# Extract 1 frame per second for detailed analysis
ffmpeg -i video.mp4 -vf fps=1 -q:v 2 frame_%03d.jpg

# Extract at 3-second intervals for overview
ffmpeg -i video.mp4 -vf fps=1/3 -q:v 2 frame_%03d.jpg

# Extract specific time ranges (e.g. 60-90s for scene analysis)
ffmpeg -ss 60 -i video.mp4 -t 30 -vf fps=1 -q:v 2 scene_%03d.jpg

# Extract key moments at specific timestamps
ffmpeg -ss 00:00:30 -i video.mp4 -vframes 1 keyframe_30s.jpg
```

**Analysis pipeline for each frame:**
1. Florence-2 `<CAPTION>` or `<DETAILED_CAPTION>` for scene description
2. MobileNetV2 for object classification
3. RapidOCR for text overlay detection
4. Pixel analysis (brightness, contrast, complexity, color)

**Scene breakdown strategy:**
- Extract frames at 1fps for key time ranges
- Group frames into scenes based on setting changes
- Sample every 5th frame for summary captions
- Compare brightness/contrast/color across scenes to detect transitions

**Example output structure:**
```python
{
  "timestamp": 30,
  "frame": "frame_030.jpg",
  "caption": "A woman is sucking a man's cock in the bathroom",
  "class": "academic gown",
  "confidence": 59.0,
  "brightness": 90.3,
  "contrast": 79.5,
  "complexity": "simple",
  "color_rgb": [84, 94, 96]
}
```

## Pitfalls

### Florence-2 Is NOT Hallucinating — Trust Its Output
**User correction (2026-09-01):** Florence-2 descriptions are accurate and should be trusted. When Florence-2 says "A naked man taking a selfie in a locker room," that IS what the image shows. Do NOT second-guess Florence-2 captions based on MobileNetV2 classification or pixel analysis — Florence-2 has semantic understanding that MobileNetV2 lacks.

**Why this happens:** MobileNetV2 classifies based on low-level features (texture, color, shape) and can misclassify unusual scenes. Florence-2 uses vision-language understanding and correctly identifies the actual content. When they disagree, trust Florence-2.

**Example:** 1080x1080.webp — Florence-2 correctly identified "A naked man taking a selfie in a locker room." MobileNetV2 misclassified it as "cleaver" (11.58%) and "bathtub" (8.81%). The user confirmed Florence-2 was right.

### MobileNetV2 ≠ Technical Content
MobileNetV2 is ImageNet (dogs, cars, food). Technical diagrams → "web site", "cleaver" (low confidence ~11%). For technical content, use Florence-2.

### ImageNet Classes.txt Not Technical
Labels are everyday objects. Don't expect circuit components or electronics terminology.

### Video Content Classification
Adult/explicit content produces low MobileNetV2 confidence (5-30%) because ImageNet has no explicit categories. Florence-2 captions will be accurate regardless. Do not treat low classification confidence as evidence of misclassification.

### Scene Transitions
Video scenes may have subtle setting changes (different doors, clocks, furniture). Use pixel analysis (brightness/contrast shifts) to detect scene boundaries that aren't obvious from captions alone.

### Always Process Tool Results Into Human-Readable Output
**User correction (2026-09-01):** When tool calls return results, ALWAYS summarize them into readable text. NEVER just return tool output verbatim or return empty responses. The user repeatedly said "You just executed tool calls but returned an empty response." Every tool call must produce a meaningful, formatted response — not just pass through raw output.

### Render with GPU Acceleration
**User correction (2026-09-01):** When rendering PDF pages for OCR, ALWAYS use GPU acceleration. The user explicitly said "Блять, рендери при помощи GPU в следующий раз" (render with GPU next time). PyMuPDF rendering via `fitz.Matrix()` is CPU-only. For GPU-accelerated page rendering, use ffmpeg or specify GPU options in the rendering pipeline.

**GPU render approach:** Render via ffmpeg with GPU encoding, or use DirectML-accelerated rendering where available.

## Scripts Location

`C:/Users/Administrator/Documents/!LAMA/scripts/`:
- `image_recognition.py` — MobileNetV2 ONNX classifier
- `florence2_recognition.py` — Florence-2 ONNX (limited — use HuggingFace instead)
- `export_florence2_onnx.py` — Attempted ONNX export (DaViT blocks it)
- `davidenko_ocr_batch.py` — Batch PDF OCR pipeline
- `davidenko_ocr_smoke.py` — OCR smoke test
- `florence2_models/full/` — Full HuggingFace model (working)

## GPU Hardware

- Intel Arc A770 4 GB (DirectX 12, DirectML)
- AMD Radeon Graphics 2 GB
- Vulkan 1.4.350
- No NVIDIA GPU present
