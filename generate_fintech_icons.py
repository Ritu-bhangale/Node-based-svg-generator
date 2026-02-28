#!/usr/bin/env python3
"""
Practical working solution: Use Stable Diffusion for icon generation.
This is the proven, reliable approach for your use case.
"""

import time
import json
from pathlib import Path
import sys

sys.path.insert(0, "/Users/ritu.bhangale/projects/Nodebased-SVG")

from benchmarks.services.diffusion_service import DiffusionService


# Fintech icon prompts
FINTECH_PROMPTS = [
    "minimalist bank transfer icon, flat design, white background, 512x512",
    "payment gateway icon, clean flat design, white background, modern",
    "cryptocurrency exchange icon, minimal style, white background",
    "investment portfolio icon, simple flat design, white background",
    "financial notification icon, minimal design, white background",
]


def generate_fintech_icons():
    """Generate fintech icons using Stable Diffusion."""
    
    print("\n" + "="*70)
    print("FINTECH ICON GENERATION - STABLE DIFFUSION PIPELINE")
    print("="*70)
    
    output_dir = Path("/Users/ritu.bhangale/projects/Nodebased-SVG/benchmarks/outputs/fintech_icons")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize service
    print("\nInitializing Stable Diffusion (first run downloads ~5GB)...")
    service = DiffusionService("stabilityai/stable-diffusion-2-1")
    service.load()
    
    results = {
        "model": "stabilityai/stable-diffusion-2-1",
        "total_prompts": len(FINTECH_PROMPTS),
        "outputs": {}
    }
    
    total_start = time.time()
    successful = 0
    
    for idx, prompt in enumerate(FINTECH_PROMPTS, 1):
        print(f"\n[{idx}/{len(FINTECH_PROMPTS)}] {prompt[:50]}...")
        
        start = time.time()
        try:
            # Generate image
            image = service.generate(
                prompt,
                steps=50,
                guidance_scale=7.5,
                height=512,
                width=512,
            )
            
            elapsed = time.time() - start
            
            # Save
            filename = f"icon_{idx}_{prompt[:20].replace(' ', '_')}.png"
            filepath = output_dir / filename
            image.save(filepath)
            
            results["outputs"][prompt] = {
                "status": "success",
                "file": str(filepath),
                "time_seconds": round(elapsed, 2),
                "size_pixels": "512x512"
            }
            
            successful += 1
            print(f"     ✓ {elapsed:.1f}s → {filename}")
            
        except Exception as e:
            results["outputs"][prompt] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"     ✗ Error: {e}")
    
    total_time = time.time() - total_start
    
    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\n✓ Generated {successful}/{len(FINTECH_PROMPTS)} icons")
    print(f"  Total time: {total_time:.1f}s ({total_time/successful:.1f}s avg)")
    print(f"  Output directory: {output_dir}")
    
    # Save results
    results_file = output_dir / "generation_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"  Results saved to: {results_file}")
    
    # Display file list
    png_files = list(output_dir.glob("*.png"))
    print(f"\nGenerated files ({len(png_files)}):")
    for f in sorted(png_files):
        print(f"  - {f.name}")
    
    return results


def next_steps():
    """Show next steps for production use."""
    
    print("\n" + "="*70)
    print("NEXT STEPS FOR PRODUCTION USE")
    print("="*70)
    
    print("""
1. VECTOR CONVERSION (Recommended)
   Convert PNG icons to SVG for scalability:
   
   $ pip install pypotrace pillow
   $ python services/svg_converter_service.py
   
   Result: Scalable SVG icons from raster generation

2. FINE-TUNING (Optional)
   Improve results with domain-specific fine-tuning:
   
   - Collect your best PNG outputs
   - Fine-tune Stable Diffusion on fintech icons
   - Use LoRA (Low-Rank Adaptation) for efficiency
   
3. INTEGRATION (Ready)
   Integrate with your frontend:
   
   a) Fast API endpoint:
      - Add /api/generate-icon endpoint
      - Return PNG or SVG
      - Cache results
   
   b) Real-time generation:
      - Background task queue (Celery)
      - Webhook callbacks
      - Progressive image delivery

4. MONITORING
   Track performance:
   
   - Generation time per prompt
   - Memory usage (MPS device)
   - Cache hit rates
   - User feedback on quality
""")


if __name__ == "__main__":
    
    # Generate icons
    results = generate_fintech_icons()
    
    # Show next steps
    next_steps()
    
    print("\n✓ Fintech icon generation pipeline ready!")
    print("  Start here: python generate_fintech_icons.py")
