"""
SVG-native LLM service for direct text-to-SVG generation.
Uses vHector-3B (preferred) or OmniSVG-4B (fallback).
"""

import logging
import re
from typing import Optional, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

# System instruction for SVG generation
SVG_SYSTEM_INSTRUCTION = """You generate SVG code. Respond with ONLY valid SVG, no text."""

# Model preference order - using code-generation optimized models
MODELS = [
    "Qwen/CodeQwen1.5-7B-Chat",  # Excellent at code generation
    "microsoft/phi-2",  # Good code generation
]


class SVGLLMService:
    """Local LLM service for SVG generation."""

    def __init__(self, model_id: Optional[str] = None) -> None:
        """
        Initialize SVG LLM service.
        
        Args:
            model_id: Model to use (defaults to trying models in preference order)
        """
        self.model_id = model_id or MODELS[0]
        self._device = self._get_device()
        self._model = None
        self._tokenizer = None
        self._loaded_model_id = None

    @staticmethod
    def _get_device() -> str:
        """Detect optimal device."""
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _get_dtype(self) -> torch.dtype:
        """Get appropriate dtype for device."""
        if self._device == "mps":
            return torch.float16
        return torch.float32

    def load(self) -> None:
        """Load model and tokenizer with fallback support."""
        if self._model is not None and self._loaded_model_id == self.model_id:
            return  # Already loaded

        # Try primary model
        try:
            self._load_model(self.model_id)
            self._loaded_model_id = self.model_id
            logger.info(f"✓ Loaded {self.model_id}")
            return
        except Exception as e:
            logger.warning(f"✗ Failed to load {self.model_id}: {e}")

        # Fallback to alternate models
        for fallback_id in MODELS:
            if fallback_id == self.model_id:
                continue
            try:
                logger.info(f"Attempting fallback: {fallback_id}")
                self._load_model(fallback_id)
                self._loaded_model_id = fallback_id
                self.model_id = fallback_id
                logger.info(f"✓ Loaded fallback {fallback_id}")
                return
            except Exception as e:
                logger.warning(f"✗ Fallback {fallback_id} failed: {e}")
                continue

        raise RuntimeError(
            f"Could not load any SVG LLM model. Tried: {MODELS}"
        )

    def _load_model(self, model_id: str) -> None:
        """Load specific model."""
        logger.info(f"Loading model: {model_id}")
        dtype = self._get_dtype()

        self._tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
        )

        self._model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )

        # Set pad token if not set
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

    def generate_svg(self, prompt: str) -> str:
        """
        Generate SVG from text prompt.
        
        Args:
            prompt: Text description of desired SVG
            
        Returns:
            Valid SVG string
            
        Raises:
            RuntimeError: If SVG generation fails
        """
        if self._model is None:
            self.load()

        # Construct direct SVG generation prompt
        full_prompt = f"Generate an SVG icon for: {prompt}\n<svg"

        # Tokenize
        inputs = self._tokenizer(
            full_prompt,
            return_tensors="pt",
            padding=True,
        ).to(self._device)

        # Generate with stricter parameters for code
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=500,
                temperature=0.3,  # Lower temp for more deterministic code
                top_p=0.8,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
            )

        # Decode
        generated_text = self._tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )

        # Prepend <svg since we started with it
        if not generated_text.strip().startswith("<svg"):
            generated_text = "<svg" + generated_text

        # Extract SVG
        svg = self._extract_svg(generated_text)

        # Validate
        if not self._is_valid_svg(svg):
            raise RuntimeError(
                f"Generated invalid SVG:\n{svg[:200]}..."
            )

        return svg

    @staticmethod
    def _extract_svg(text: str) -> str:
        """Extract SVG content from generated text."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:svg|xml)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        # Find SVG tags
        start = text.find("<svg")
        end = text.rfind("</svg>")

        if start == -1 or end == -1:
            return ""

        return text[start : end + 6].strip()

    @staticmethod
    def _is_valid_svg(svg: str) -> bool:
        """Validate SVG structure."""
        if not svg:
            return False
        if not svg.startswith("<svg"):
            return False
        if not svg.endswith("</svg>"):
            return False
        if svg.count("<svg") > 1:
            return False
        return True

    @property
    def device(self) -> str:
        """Get current device."""
        return self._device

    @property
    def loaded_model(self) -> str:
        """Get loaded model ID."""
        return self._loaded_model_id or self.model_id
