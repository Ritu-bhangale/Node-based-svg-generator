import os
import logging

import httpx

from services.debug_utils import compact_json, truncate_text
from services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": system_prompt + "\n\n" + user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 8192,
                # Disable internal reasoning tokens so the response budget is
                # used for visible structured outputs (JSON/SVG).
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }

        logger.info(
            "gemini.request model=%s temperature=%.2f payload=%s",
            self.model,
            temperature,
            compact_json(payload, limit=2500),
        )
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                logger.info("gemini.response.http_status=%s", response.status_code)
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError as exc:
            logger.exception("gemini.connect_error model=%s error=%s", self.model, exc)
            raise ValueError(
                "Gemini connection failed (DNS/network). "
                "Check internet access, VPN/firewall, and proxy settings."
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.exception("gemini.http_error model=%s status=%s", self.model, exc.response.status_code)
            raise ValueError(f"Gemini HTTP error: {exc.response.status_code} {exc.response.text}") from exc
        logger.info("gemini.response.body=%s", compact_json(data, limit=2500))

        if "candidates" not in data or not data["candidates"]:
            raise ValueError("Gemini returned no candidates")
        candidate = data["candidates"][0]
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
        finish_reason = candidate.get("finishReason")
        if not text:
            raise ValueError(f"Gemini returned empty content (finishReason={finish_reason})")
        if finish_reason == "MAX_TOKENS":
            logger.warning("gemini.response.truncated finishReason=%s", finish_reason)
        logger.info("gemini.response.text=%s", truncate_text(text, limit=2500))
        return text
