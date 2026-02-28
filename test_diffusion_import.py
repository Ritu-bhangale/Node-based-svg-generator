#!/usr/bin/env python3
"""Quick test to check diffusion imports."""

import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    print("\n1. Testing torch...")
    import torch
    print(f"   ✓ torch {torch.__version__}")
    print(f"   Device: cuda={torch.cuda.is_available()}, mps={getattr(torch.backends, 'mps', None) is not None}")
except Exception as e:
    print(f"   ✗ torch failed: {e}")
    sys.exit(1)

try:
    print("\n2. Testing transformers...")
    import transformers
    print(f"   ✓ transformers {transformers.__version__}")
except Exception as e:
    print(f"   ✗ transformers failed: {e}")
    sys.exit(1)

try:
    print("\n3. Testing diffusers...")
    import diffusers
    print(f"   ✓ diffusers {diffusers.__version__}")
except Exception as e:
    print(f"   ✗ diffusers failed: {e}")
    sys.exit(1)

try:
    print("\n4. Testing PIL...")
    from PIL import Image
    print(f"   ✓ PIL/Pillow ready")
except Exception as e:
    print(f"   ✗ PIL failed: {e}")
    sys.exit(1)

print("\n✓ All imports successful. Ready for benchmarking.")
