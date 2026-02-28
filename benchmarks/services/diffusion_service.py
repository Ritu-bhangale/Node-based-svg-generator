"""
Diffusion service for icon generation. Isolated from StarVector/svg-engine.
"""

import re
from typing import Optional

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image


PROMPT_PREFIX = (
    "flat vector icon, minimal, solid shapes, no gradients, no shading, no texture, "
    "white background, centered composition, simple geometry, "
)


class DiffusionService:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self._device = self._get_device()
        self._pipe: Optional[StableDiffusionPipeline] = None

    @staticmethod
    def _get_device() -> str:
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def load(self) -> None:
        if self._pipe is not None:
            return
        self._pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float32,
            safety_checker=None,
        )
        self._pipe = self._pipe.to(self._device)
        self._pipe.enable_attention_slicing()

    def generate(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5,
    ) -> Image.Image:
        if self._pipe is None:
            self.load()
        full_prompt = PROMPT_PREFIX + (prompt.strip() or "icon")
        out = self._pipe(
            prompt=full_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )
        images = out.images
        if not images:
            raise RuntimeError("Diffusion pipeline returned no images")
        return images[0]
