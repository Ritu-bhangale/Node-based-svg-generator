#!/usr/bin/env python3
"""
Quick benchmark test with a smaller model.
Tests the pipeline infrastructure before running full benchmark.
"""

import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from benchmarks.services.diffusion_service import DiffusionService

OUTPUTS_DIR = Path("benchmarks/outputs/test")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Use a smaller, faster model for testing
TEST_MODEL = "milyiyo/flat-design-icons"
TEST_PROMPTS = [
    "minimal bank icon",
    "simple transfer symbol",
]

print(f"\n{'='*60}")
print(f"DIFFUSION BENCHMARK - QUICK TEST")
print(f"{'='*60}\n")

print(f"Model: {TEST_MODEL}")
print(f"Device: checking...")

service = DiffusionService(TEST_MODEL)
print(f"Loading model (this downloads ~2-4GB on first run)...")

try:
    service.load()
    print(f"✓ Model loaded successfully")
    print(f"✓ Device: {service._device}")
    print(f"✓ Attention slicing enabled\n")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    sys.exit(1)

print(f"Generating {len(TEST_PROMPTS)} test icons...")
print(f"Output: {OUTPUTS_DIR}\n")

times = []
for i, prompt in enumerate(TEST_PROMPTS, 1):
    try:
        print(f"{i}. Generating: '{prompt}'...")
        start = time.perf_counter()
        image = service.generate(
            prompt,
            width=512,
            height=512,
            num_inference_steps=25,
            guidance_scale=7.5,
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        
        filename = f"test_{i}.png"
        filepath = OUTPUTS_DIR / filename
        image.save(filepath)
        print(f"   ✓ {elapsed:.2f}s -> {filepath}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        sys.exit(1)

print(f"\n{'='*60}")
print(f"RESULTS")
print(f"{'='*60}")
print(f"Total time: {sum(times):.2f}s")
print(f"Average per image: {sum(times)/len(times):.2f}s")
print(f"✓ Quick test completed successfully!")
print(f"✓ Ready for full benchmark run\n")
