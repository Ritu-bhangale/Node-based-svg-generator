#!/usr/bin/env python3
"""Test SVG LLM service imports."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

print("Testing SVG LLM service imports...\n")

try:
    print("1. Checking torch...")
    import torch
    print(f"   ✓ torch {torch.__version__}")
    print(f"   Device: MPS={torch.backends.mps.is_available()}")
except Exception as e:
    print(f"   ✗ torch failed: {e}")
    sys.exit(1)

try:
    print("\n2. Checking transformers...")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"   ✓ transformers ready")
except Exception as e:
    print(f"   ✗ transformers failed: {e}")
    sys.exit(1)

try:
    print("\n3. Importing SVGLLMService...")
    from services.svg_llm_service import SVGLLMService
    print(f"   ✓ SVGLLMService imported")
except Exception as e:
    print(f"   ✗ SVGLLMService import failed: {e}")
    sys.exit(1)

try:
    print("\n4. Instantiating service...")
    service = SVGLLMService()
    print(f"   ✓ Service created")
    print(f"   Device: {service.device}")
    print(f"   Model: {service.model_id}")
except Exception as e:
    print(f"   ✗ Service instantiation failed: {e}")
    sys.exit(1)

print("\n✓ All imports successful. Ready for benchmarking.\n")
