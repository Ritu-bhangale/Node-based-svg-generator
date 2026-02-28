"""
Test SVG LLM generation pipeline.
Run: python benchmarks/test_svg_llm.py
"""

import re
import sys
import time
from pathlib import Path

# Add project root to path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from services.svg_llm_service import SVGLLMService

OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs" / "svg_llm"

PROMPTS = [
    "bank transfer icon",
    "minimal fintech payment icon",
    "switch transfer symbol",
    "notification bell icon",
    "premium investment logo",
]


def slug(text: str) -> str:
    """Convert text to slug."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s[:64] or "prompt"


def main() -> None:
    """Run SVG LLM benchmark."""
    print("\n" + "=" * 70)
    print("SVG LLM GENERATION BENCHMARK")
    print("=" * 70)

    # Create output directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize service
    print("\nInitializing SVG LLM service...")
    service = SVGLLMService()
    print(f"Device: {service.device}")

    # Load model
    print("Loading model (first run downloads ~6-10GB)...")
    try:
        service.load()
        print(f"✓ Loaded: {service.loaded_model}\n")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        sys.exit(1)

    # Generate SVGs
    print(f"Generating {len(PROMPTS)} SVG icons...\n")
    times = []
    generated_count = 0

    for i, prompt in enumerate(PROMPTS, 1):
        prompt_slug = slug(prompt)
        out_path = OUTPUTS_DIR / f"{prompt_slug}.svg"

        try:
            print(f"{i}. {prompt}")
            start = time.perf_counter()
            svg = service.generate_svg(prompt)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

            # Save SVG
            out_path.write_text(svg, encoding="utf-8")
            generated_count += 1

            # Get token count (approximate)
            tokens = len(svg.split())
            print(f"   ✓ {elapsed:.2f}s ({tokens} tokens)")
            print(f"   → {out_path}\n")

        except Exception as e:
            print(f"   ✗ Failed: {e}\n")

    # Report
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Generated: {generated_count}/{len(PROMPTS)}")
    if times:
        print(f"Total time: {sum(times):.2f}s")
        print(f"Average per SVG: {sum(times)/len(times):.2f}s")
        print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")
    print(f"Output: {OUTPUTS_DIR}/\n")


if __name__ == "__main__":
    main()
