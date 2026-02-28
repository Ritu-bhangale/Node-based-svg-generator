"""
Diffusion benchmarking pipeline. Run from repo root:

    python benchmarks/benchmark_diffusion.py

Requires: pip install -r benchmarks/requirements.txt
"""

import re
import sys
import time
from pathlib import Path

# Ensure repo root is on path when run as script
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from benchmarks.services.diffusion_service import DiffusionService


BENCHMARKS_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BENCHMARKS_DIR / "outputs"

MODELS = [
    "milyiyo/flat-design-icons",
    "nicky007/stable-diffusion-logo-fine-tuned",
    "proximasanfinetuning/fantassified-icons-v2",
]

PROMPTS = [
    "bank transfer icon",
    "minimal fintech payment icon",
    "switch transfer symbol",
    "notification bell icon",
    "premium investment logo",
]

WIDTH = 512
HEIGHT = 512
NUM_INFERENCE_STEPS = 25
GUIDANCE_SCALE = 7.5


def slug(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s[:64] or "prompt"


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    for model_id in MODELS:
        model_name = model_id.replace("/", "_")
        model_out = OUTPUTS_DIR / model_name
        model_out.mkdir(parents=True, exist_ok=True)

        print(f"\n=== Model: {model_id} ===")
        service = DiffusionService(model_id)
        service.load()

        for prompt in PROMPTS:
            prompt_slug = slug(prompt)
            out_path = model_out / f"{prompt_slug}.png"

            start = time.perf_counter()
            image = service.generate(
                prompt,
                width=WIDTH,
                height=HEIGHT,
                num_inference_steps=NUM_INFERENCE_STEPS,
                guidance_scale=GUIDANCE_SCALE,
            )
            elapsed = time.perf_counter() - start

            image.save(out_path)
            print(f"  {prompt_slug}.png  {elapsed:.2f}s  ->  {out_path}")

    print("\nDone. Outputs under benchmarks/outputs/")


if __name__ == "__main__":
    main()
