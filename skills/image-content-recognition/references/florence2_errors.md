# Florence-2 Error Transcript (2026-09-01)

Complete session log of all attempts to get Florence-2 working, with exact fixes.

## Environment

- PyTorch: 2.4.1+cpu (downgraded from 2.8.0)
- Torchvision: 0.19.1+cpu (downgraded from 0.23.0+)
- Transformers: 4.57.6 (downgraded from 5.16.1)
- einops: 0.8.2
- onnxruntime-directml: 1.24.4
- Cache: C:/Users/Administrator/AppData/Local/hermes/cache/hf/

## Working Solution: HuggingFace transformers

```python
from transformers import AutoModelForCausalLM, AutoProcessor
import torch
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True,
    cache_dir="C:/Users/Administrator/AppData/Local/hermes/cache/hf",
    low_cpu_mem_usage=True,
    attn_implementation="eager"  # REQUIRED
)
processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-base",
    trust_remote_code=True,
    cache_dir="C:/Users/Administrator/AppData/Local/hermes/cache/hf"
)

# Manual autoregressive loop (model.generate() has past_key_values bug)
inputs = processor(text="<CAPTION>", images=img, return_tensors="pt")
generated_ids = list(inputs["input_ids"][0].tolist())
with torch.no_grad():
    for step in range(50):
        outputs = model(
            decoder_input_ids=torch.tensor([generated_ids]),
            pixel_values=inputs["pixel_values"],
            return_dict=True
        )
        next_id = outputs.logits[0, -1].argmax().item()
        generated_ids.append(next_id)
        if next_id in [processor.tokenizer.eos_token_id, 2]:
            break
caption = processor.tokenizer.decode(generated_ids, skip_special_tokens=True)
```

## All Errors Encountered (in order)

1. `ImportError: Could not import module 'AutoProcessor'` — transformers 5.16.1 broken
   - Fix: `uv pip install "transformers>=4.40,<5.0"`

2. `ImportError: Could not import module 'pipeline'` — transformers 5.16.1 API mismatch
   - Fix: same as above

3. `RuntimeError: operator torchvision::nms does not exist` — torch 2.8.0 + torchvision mismatch
   - Fix: `uv pip install torch==2.4.1 torchvision==0.19.1`

4. `ModuleNotFoundError: No module named 'einops'` — missing dependency
   - Fix: `uv pip install einops`

5. `AttributeError: '_supports_sdpa'` — SDPA incompatible with Florence-2
   - Fix: `attn_implementation="eager"`

6. `AttributeError: 'Florence2ForConditionalGeneration' object has no attribute 'vision_model'` — model has `vision_tower` not `vision_model`
   - Fix: use `model.vision_tower`

7. `AttributeError: 'DaViT' object has no attribute 'norms'` — DaViT internal structure blocks ONNX export
   - Fix: ONNX export not possible, use transformers

8. `AttributeError: 'Florence2ForConditionalGeneration' object has no attribute 'encoder'` — model has no separate encoder
   - Fix: encoder is embedded in vision_tower

9. `TypeError: DaViT.forward() got an unexpected keyword argument 'pixel_values'` — wrong input method
   - Fix: use `vision_tower(pixel_values=...)` not `vision_model(pixel_values=...)`

10. `ValueError: If no decoder_input_ids or decoder_inputs_embeds are passed, input_ids cannot be None` — wrong forward call
    - Fix: use `decoder_input_ids` not `input_ids`

11. `AssertionError: Task token <CAPTION> should be the only token` — added bos_token prefix
    - Fix: use only `"<CAPTION>"` not `bos_token + "<CAPTION>"`

12. `AttributeError: 'NoneType' object has no attribute 'shape'` on model.generate() — past_key_values=None bug
    - Fix: manual autoregressive loop instead of generate()

13. ONNX `InsertedPrecisionFreeCast_/blocks.1/blocks.1.0/channel_block/ffn/norm/Constant_output_0` — graph fusion error
    - Fix: use HuggingFace transformers, ONNX export not possible with this onnxruntime

## ONNX Export Attempted

- Exported to `C:/Users/Administrator/Documents/!LAMA/scripts/export_florence2_onnx.py`
- Failed at vision encoder export (DaViT internal norms attribute)
- Full model saved via `model.save_pretrained()` to `florence2_models/full/`
- ONNX export not viable with current onnxruntime (1.26+) + DaViT architecture

## Install Command (exact working)

```bash
uv pip install torch==2.4.1 torchvision==0.19.1 einops
uv pip install "transformers>=4.40,<5.0"
```

## Note: transformers 4.57.6

Version 4.57.6 was installed via `uv pip install "transformers>=4.40,<5.0"`. Earlier attempt with pip 5.16.1 failed. Do NOT install latest transformers.
