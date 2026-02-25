import json
import logging
from typing import Any

from services.debug_utils import compact_json, truncate_text
from services.llm_provider import LLMProvider
from services.prompts import svg_generator_system_prompt

logger = logging.getLogger(__name__)


class SVGGenerationService:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def generate_svg(self, plan: dict[str, Any], original_svg: str | None = None) -> tuple[str, dict[str, Any]]:
        user_payload: dict[str, Any] = {
            "plan": plan,
        }
        if original_svg is not None:
            user_payload["originalSvg"] = original_svg

        user_prompt = json.dumps(user_payload)
        logger.info(
            "svg_generator.request system_prompt=%s user_payload=%s",
            truncate_text(svg_generator_system_prompt, limit=1200),
            compact_json(user_payload, limit=2500),
        )
        raw = await self.llm.generate(
            system_prompt=svg_generator_system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
        )
        logger.info("svg_generator.response.raw=%s", truncate_text(raw, limit=2500))
        extracted = self._extract_single_svg(raw)
        logger.info("svg_generator.response.extracted=%s", truncate_text(extracted, limit=2500))
        debug_payload: dict[str, Any] = {
            "request": user_payload,
            "rawResponse": raw,
            "extracted": extracted,
        }
        return extracted, debug_payload

    @staticmethod
    def _extract_single_svg(raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            if len(parts) >= 3:
                cleaned = parts[1].strip()
                first_newline = cleaned.find("\n")
                if first_newline != -1:
                    maybe_lang = cleaned[:first_newline].strip().lower()
                    if maybe_lang in {"svg", "xml", "html", "text"}:
                        cleaned = cleaned[first_newline + 1 :].strip()
            else:
                cleaned = cleaned.replace("```", "").strip()

        start = cleaned.find("<svg")
        end = cleaned.rfind("</svg>")
        if start == -1 or end == -1:
            if cleaned.find("<svg") != -1 and cleaned.rfind("</svg>") == -1:
                raise ValueError("Generator returned incomplete SVG (likely truncated by token limit)")
            raise ValueError("Generator did not return valid SVG root")

        if cleaned.count("<svg") > 1:
            raise ValueError("Generator returned multiple SVG roots")

        return cleaned[start : end + 6].strip()
