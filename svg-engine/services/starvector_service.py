import logging
import time
from typing import Optional

import torch
from transformers import AutoModelForCausalLM


logger = logging.getLogger(__name__)


class StarVectorService:
    def __init__(self) -> None:
        self.model = None
        self.processor = None
        self.device: Optional[torch.device] = None
        self._loaded: bool = False

    def _detect_device(self) -> torch.device:
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def load(self) -> None:
        if self._loaded:
            return

        start = time.perf_counter()
        self.device = self._detect_device()
        logger.info("starvector.load.start device=%s", self.device)

        dtype = None
        if self.device.type == "cuda":
            dtype = torch.float16

        model = AutoModelForCausalLM.from_pretrained(
            "starvector/starvector-1b-im2svg",
            trust_remote_code=True,
            torch_dtype=dtype,
        )
        model.to(self.device)
        model.eval()

        self.model = model
        # The StarVector repository exposes a processor on the model instance
        self.processor = getattr(model, "processor", None)
        self._loaded = True

        # Temporary debug: inspect StarVector model structure
        print("=== MODEL TYPE ===")
        print(type(self.model))

        print("\n=== MODEL DIR ===")
        print(dir(self.model))

        inner = getattr(self.model, "model", None)
        print("\n=== INNER MODEL DIR ===")
        print(dir(inner) if inner is not None else "None")

        print("\n=== HAS generate_im2svg ===", hasattr(self.model, "generate_im2svg"))
        print("=== HAS generate_text2svg ===", hasattr(self.model, "generate_text2svg"))
        print("=== HAS generate ===", hasattr(self.model, "generate"))

        elapsed = time.perf_counter() - start
        logger.info("starvector.load.success device=%s elapsed=%.2fs", self.device, elapsed)

    async def generate(self, prompt: str) -> str:
        if not self._loaded or self.model is None:
            raise RuntimeError("StarVector model not loaded. Call load() at startup.")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")

        # StarVector expects a batch dict. For this project we treat prompt as text input.
        batch = {"text": prompt.strip()}

        def _run_inference() -> str:
            start = time.perf_counter()
            with torch.no_grad():
                outputs = self.model.generate_im2svg(batch, max_length=1000)
            elapsed = time.perf_counter() - start
            logger.info("starvector.generate.success device=%s elapsed=%.2fs", self.device, elapsed)
            if isinstance(outputs, str):
                return outputs
            # Fallback if the model returns a list or dict-like structure
            if isinstance(outputs, (list, tuple)) and outputs:
                return str(outputs[0])
            return str(outputs)

        # Run blocking HF generation in a thread to avoid blocking the event loop.
        import asyncio

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _run_inference)


starvector_service = StarVectorService()

