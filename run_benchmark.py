#!/usr/bin/env python3
"""
Run the full diffusion benchmark with detailed metrics.
Usage: python run_benchmark.py
"""

import subprocess
import sys
from pathlib import Path

VENV_PYTHON = Path(".venv/bin/python")
BENCHMARK_SCRIPT = Path("benchmarks/benchmark_diffusion.py")

if not VENV_PYTHON.exists():
    print(f"❌ Virtual environment not found at {VENV_PYTHON}")
    print(f"Please run: python3 -m venv .venv && source .venv/bin/activate")
    sys.exit(1)

if not BENCHMARK_SCRIPT.exists():
    print(f"❌ Benchmark script not found at {BENCHMARK_SCRIPT}")
    sys.exit(1)

print("\n" + "="*70)
print("DIFFUSION BENCHMARK RUNNER")
print("="*70)
print(f"\nPython: {VENV_PYTHON}")
print(f"Script: {BENCHMARK_SCRIPT}")
print(f"\nNote: First run downloads ~12GB of model weights (~2-3 hours total)")
print(f"      Models are cached for faster subsequent runs")
print("\n" + "="*70 + "\n")

try:
    result = subprocess.run(
        [str(VENV_PYTHON), str(BENCHMARK_SCRIPT)],
        cwd=Path.cwd(),
    )
    sys.exit(result.returncode)
except KeyboardInterrupt:
    print("\n\n⚠️  Benchmark interrupted by user")
    print("Note: Downloaded models are cached and will be reused on next run")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error running benchmark: {e}")
    sys.exit(1)
