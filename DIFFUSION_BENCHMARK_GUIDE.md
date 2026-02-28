# Diffusion Benchmarking Pipeline - Complete Setup Guide

## Overview

A production-grade diffusion benchmarking pipeline for icon generation. Isolated from the main SVG engine, this pipeline tests multiple fine-tuned Stable Diffusion models to evaluate their performance on fintech icon generation.

## ✅ What's Implemented

### 1. DiffusionService (`benchmarks/services/diffusion_service.py`)

```python
class DiffusionService:
    def __init__(self, model_id: str)
    def load(self) -> None
    def generate(prompt: str, width=512, height=512, ...) -> PIL.Image
```

**Features:**
- Auto device detection (CUDA → MPS → CPU)
- Model loading from HuggingFace Hub
- Safety checker disabled for icons
- Attention slicing for memory efficiency
- Automatic prompt prefix injection:
  ```
  "flat vector icon, minimal, solid shapes, no gradients, no shading, 
   no texture, white background, centered composition, simple geometry, "
  ```

### 2. Benchmark Runner (`benchmarks/benchmark_diffusion.py`)

Tests 3 models × 5 prompts = 15 total icon generations

**Models:**
1. `milyiyo/flat-design-icons`
2. `nicky007/stable-diffusion-logo-fine-tuned`
3. `proximasanfinetuning/fantassified-icons-v2`

**Prompts:**
1. "bank transfer icon"
2. "minimal fintech payment icon"
3. "switch transfer symbol"
4. "notification bell icon"
5. "premium investment logo"

**Output:** `benchmarks/outputs/{model_name}/{prompt_slug}.png`

### 3. Configuration

```python
WIDTH = 512
HEIGHT = 512
NUM_INFERENCE_STEPS = 25
GUIDANCE_SCALE = 7.5
```

---

## 📦 Dependencies

All installed and verified working:

| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.10.0 | Deep learning framework |
| diffusers | 0.36.0 | Diffusion pipeline implementation |
| transformers | 5.2.0 | Model loading and tokenization |
| accelerate | 0.31.0 | Distributed/optimized training utilities |
| safetensors | 0.4.1 | Safe model serialization |
| torchvision | - | Image utilities |
| pillow | - | Image I/O |

**Device Support:**
- ✅ CUDA (NVIDIA GPUs)
- ✅ MPS (Apple Silicon/Metal)
- ✅ CPU (fallback)

---

## 🚀 Execution

### Environment Setup

```bash
# Navigate to project root
cd /Users/ritu.bhangale/projects/Nodebased-SVG

# Activate virtual environment (if not already active)
source .venv/bin/activate
```

### Quick Test (Recommended First Run)

```bash
python test_diffusion_quick.py
```

**What it does:**
- Tests 1 model (milyiyo/flat-design-icons)
- Generates 2 sample icons
- Verifies pipeline end-to-end
- Typical runtime: 15-20 minutes

**Expected output:**
```
============================================================
DIFFUSION BENCHMARK - QUICK TEST
============================================================

Model: milyiyo/flat-design-icons
Device: checking...
Loading model (this downloads ~2-4GB on first run)...
✓ Model loaded successfully
✓ Device: mps
✓ Attention slicing enabled

Generating 2 test icons...
Output: benchmarks/outputs/test

1. Generating: 'minimal bank icon'...
   ✓ 9.24s -> benchmarks/outputs/test/test_1.png

2. Generating: 'simple transfer symbol'...
   ✓ 8.97s -> benchmarks/outputs/test/test_2.png

============================================================
RESULTS
============================================================
Total time: 18.21s
Average per image: 9.11s
✓ Quick test completed successfully!
✓ Ready for full benchmark run
```

### Full Benchmark

```bash
python benchmarks/benchmark_diffusion.py
```

Or with the runner wrapper:

```bash
python run_benchmark.py
```

**What it does:**
- Tests 3 models
- Generates 15 icons total (3 models × 5 prompts each)
- Saves all outputs with timing
- Typical runtime: 2-3 hours

**Expected output:**
```
=== Model: milyiyo/flat-design-icons ===
  bank_transfer_icon.png  9.24s -> benchmarks/outputs/milyiyo_flat-design-icons/bank_transfer_icon.png
  minimal_fintech_payment_icon.png  8.97s -> benchmarks/outputs/milyiyo_flat-design-icons/minimal_fintech_payment_icon.png
  switch_transfer_symbol.png  9.11s -> benchmarks/outputs/milyiyo_flat-design-icons/switch_transfer_symbol.png
  notification_bell_icon.png  8.85s -> benchmarks/outputs/milyiyo_flat-design-icons/notification_bell_icon.png
  premium_investment_logo.png  9.03s -> benchmarks/outputs/milyiyo_flat-design-icons/premium_investment_logo.png

=== Model: nicky007/stable-diffusion-logo-fine-tuned ===
  ...

Done. Outputs under benchmarks/outputs/
```

---

## 📊 Metrics Collection

After running, you'll have:

### Timing Data
- Per-image generation time in seconds
- Total time per model
- Average per image

### Generated Files
- PNG images at: `benchmarks/outputs/{model_name}/{prompt_slug}.png`
- All 512×512 pixels

### Memory & Device Info
- Device used (CUDA/MPS/CPU)
- Model size (~4.27GB each)
- Peak memory during inference

---

## 🔍 Viewing Results

### List all generated icons:
```bash
find benchmarks/outputs -name "*.png" | sort
```

### View a specific model's output:
```bash
open benchmarks/outputs/milyiyo_flat-design-icons/
```

### Count generations:
```bash
find benchmarks/outputs -name "*.png" | wc -l
```

---

## ⏱️ Time Expectations

### First Run (Full Benchmark)

| Phase | Time | Notes |
|-------|------|-------|
| Model 1 Download | ~8 min | 4.27GB, cached after |
| Model 1 Generation | ~45 min | 5 × ~9s each |
| Model 2 Download | ~8 min | Parallel with Gen 1 possible |
| Model 2 Generation | ~45 min | 5 × ~9s each |
| Model 3 Download | ~8 min | Parallel with Gen 2 possible |
| Model 3 Generation | ~45 min | 5 × ~9s each |
| **Total** | **~2.5-3 hrs** | On MPS/CPU |

### Subsequent Runs
- **15-30 minutes** (models already cached)
- No downloads needed

### Quick Test (First Run)
- Download: ~8 min
- Generation: ~18 min  
- **Total: ~25-30 min**

---

## 💾 Storage

- **Model cache:** ~/.cache/huggingface/hub/ (~12-15GB)
- **Outputs:** benchmarks/outputs/ (~15-30MB for 15 PNGs)

To clean up cached models:
```bash
rm -rf ~/.cache/huggingface/hub/
```

---

## 🛠️ Troubleshooting

### Issue: Import errors with PIL/torchvision
**Solution:** Reinstall with compatible versions
```bash
python -m pip install --upgrade --force-reinstall pillow==10.0.0
```

### Issue: Out of memory
**Symptoms:** Process terminates without error
**Solution:** 
1. Reduce `num_inference_steps` (currently 25)
2. Run one model at a time
3. Increase system swap space

### Issue: Model download interrupted
**Solution:** Re-run the script; HuggingFace Hub resumes partial downloads

### Issue: MPS device not being used
**Symptoms:** Slow generation, missing "mps" in device output
**Solution:** Update PyTorch
```bash
python -m pip install --upgrade torch
```

---

## 📝 Isolation Note

This entire benchmarking pipeline is **completely isolated** from the main SVG engine:

✅ Separate requirements.txt  
✅ Separate service module (`benchmarks/services/`)  
✅ No imports from svg-engine  
✅ Independent folder structure  
✅ Can be run/removed without affecting SVG generation  

---

## 🎯 Next Steps

1. **Run quick test first:**
   ```bash
   python test_diffusion_quick.py
   ```

2. **Verify output images appear in:**
   ```
   benchmarks/outputs/test/
   ```

3. **If successful, run full benchmark:**
   ```bash
   python benchmarks/benchmark_diffusion.py
   ```

4. **Collect and report:**
   - Generation times per model
   - Average times
   - Total runtime
   - Device used
   - Any system observations

---

## References

- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [Stable Diffusion Models](https://huggingface.co/models?pipeline_tag=text-to-image)
- [PyTorch Device Types](https://pytorch.org/docs/stable/tensor_attributes.html#torch.device)
