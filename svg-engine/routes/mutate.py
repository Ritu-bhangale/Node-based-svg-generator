import logging
import os

from fastapi import APIRouter, HTTPException

from schemas.mutation_schema import MutateRequest, MutateResponse
from services.debug_utils import compact_json, truncate_text
from services.llm_provider import get_llm_metadata, get_llm_provider
from services.planner_service import PlannerService
from services.svg_generation_service import SVGGenerationService
from services.svg_normalizer import SVGNormalizer
from services.svg_validator import SVGValidator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/mutate", response_model=MutateResponse)
async def mutate_svg(payload: MutateRequest) -> MutateResponse:
    logger.info(
        "route.mutate.request userInput=%s svg=%s",
        truncate_text(payload.userInput, limit=500),
        truncate_text(payload.svg, limit=1500),
    )
    llm = get_llm_provider()
    planner_service = PlannerService(llm)
    svg_generation_service = SVGGenerationService(llm)
    debug_enabled = os.getenv("DEBUG_LLM", "false").lower() in {"1", "true", "yes", "on"}
    llm_meta = get_llm_metadata()

    normalized_input = SVGNormalizer.normalize(payload.svg, strip_transforms=False)
    SVGValidator.validate_svg(normalized_input)
    logger.info("route.mutate.normalized_input=%s", truncate_text(normalized_input, limit=2000))

    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            logger.info("route.mutate.attempt.start=%s", attempt)
            plan, planner_debug = await planner_service.plan_mutate(
                user_input=payload.userInput,
                original_svg=normalized_input,
            )
            logger.info("route.mutate.plan=%s", compact_json(plan, limit=2000))
            raw_svg, generator_debug = await svg_generation_service.generate_svg(
                plan=plan,
                original_svg=normalized_input,
            )
            cleaned_svg = SVGValidator.strip_markdown_fences(raw_svg)
            normalized_output = SVGNormalizer.normalize(cleaned_svg, strip_transforms=False)
            SVGValidator.validate_svg(normalized_output)
            logger.info("route.mutate.success attempt=%s svg=%s", attempt, truncate_text(normalized_output, limit=2000))
            debug_payload: dict[str, object] | None = None
            if debug_enabled:
                debug_payload = {
                    "provider": llm_meta["provider"],
                    "model": llm_meta["model"],
                    "planner": planner_debug,
                    "generator": generator_debug,
                    "normalizedSvg": normalized_output,
                }
            return MutateResponse(svg=normalized_output, debug=debug_payload)
        except Exception as exc:
            last_error = exc
            logger.exception("route.mutate.attempt.failed=%s error=%s", attempt, exc)

    logger.error("route.mutate.failed after_retries error=%s", last_error)
    raise HTTPException(status_code=400, detail=f"mutate_failed: {last_error}")
