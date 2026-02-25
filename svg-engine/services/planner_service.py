import json
import logging
from typing import Any

from services.debug_utils import compact_json, truncate_text
from services.llm_provider import LLMProvider
from services.prompts import planner_system_prompt

logger = logging.getLogger(__name__)


class PlannerService:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def plan_generate(self, prompt: str, brand_constraints: dict[str, Any], variant_index: int) -> tuple[dict[str, Any], dict[str, Any]]:
        user_payload = {
            "mode": "generate",
            "prompt": prompt,
            "brandConstraints": brand_constraints,
            "variantIndex": variant_index,
            "instruction": "Create a distinct icon concept for this variant index.",
        }
        return await self._generate_plan(user_payload)

    async def plan_mutate(self, user_input: str, original_svg: str) -> tuple[dict[str, Any], dict[str, Any]]:
        user_payload = {
            "mode": "mutate",
            "userInput": user_input,
            "originalSvg": original_svg,
            "instruction": "Plan a structural mutation as strict JSON for downstream SVG generation.",
        }
        return await self._generate_plan(user_payload)

    async def _generate_plan(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        user_prompt = json.dumps(payload)
        logger.info(
            "planner.request system_prompt=%s user_prompt=%s",
            truncate_text(planner_system_prompt, limit=1200),
            truncate_text(user_prompt, limit=2000),
        )
        raw = await self.llm.generate(
            system_prompt=planner_system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
        )
        logger.info("planner.response.raw=%s", truncate_text(raw, limit=2500))
        cleaned = self._strip_markdown_fences(raw)
        logger.info("planner.response.cleaned=%s", truncate_text(cleaned, limit=2500))
        parsed = self._extract_json_object(cleaned)
        self._validate_plan_schema(parsed)
        logger.info("planner.response.parsed=%s", compact_json(parsed, limit=2500))
        debug_payload: dict[str, Any] = {
            "request": payload,
            "rawResponse": raw,
            "parsed": parsed,
        }
        return parsed, debug_payload

    @staticmethod
    def _strip_markdown_fences(raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            if len(parts) >= 3:
                cleaned = parts[1].strip()
                first_newline = cleaned.find("\n")
                if first_newline != -1:
                    maybe_lang = cleaned[:first_newline].strip().lower()
                    if maybe_lang in {"json", "javascript", "js", "text"}:
                        cleaned = cleaned[first_newline + 1 :].strip()
            else:
                cleaned = cleaned.replace("```", "").strip()
        return cleaned

    @staticmethod
    def _extract_json_object(text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ValueError("Planner returned non-JSON output")
            parsed = json.loads(text[start : end + 1])

        if not isinstance(parsed, dict):
            raise ValueError("Planner output must be a JSON object")
        return parsed

    @staticmethod
    def _validate_plan_schema(plan: dict[str, Any]) -> None:
        mode = plan.get("mode")
        if mode not in {"generate", "mutate"}:
            raise ValueError("Planner output must include mode = generate|mutate")

        if mode == "generate":
            elements = plan.get("elements")
            style = plan.get("style")
            if not isinstance(elements, list) or len(elements) == 0:
                raise ValueError("Generate plan must include non-empty elements list")
            if not isinstance(style, dict):
                raise ValueError("Generate plan must include style object")
            return

        mutation_intent = plan.get("mutationIntent")
        if not isinstance(mutation_intent, str) or not mutation_intent.strip():
            raise ValueError("Mutate plan must include mutationIntent")

        target = plan.get("target")
        description = plan.get("description")
        has_target = isinstance(target, str) and bool(target.strip())
        has_description = isinstance(description, str) and len(description.strip()) >= 8
        if not (has_target or has_description):
            raise ValueError("Mutate plan must include target or sufficient description")
