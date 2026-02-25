import logging
import os

from fastapi import APIRouter, HTTPException

from schemas.layout_schema import GenerateRequest, GenerateResponse, Variant
from services.debug_utils import compact_json, truncate_text
from services.llm_provider import get_llm_metadata, get_llm_provider
from services.planner_service import PlannerService
from services.svg_generation_service import SVGGenerationService
from services.svg_normalizer import SVGNormalizer
from services.svg_validator import SVGValidator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=GenerateResponse)
async def generate_icons(payload: GenerateRequest) -> GenerateResponse:
    logger.info("route.generate.request=%s", compact_json(payload.model_dump(), limit=2000))
    llm = get_llm_provider()
    planner_service = PlannerService(llm)
    svg_generation_service = SVGGenerationService(llm)
    debug_enabled = os.getenv("DEBUG_LLM", "false").lower() in {"1", "true", "yes", "on"}
    llm_meta = get_llm_metadata()

    try:
        variants: list[Variant] = []
        debug_variants: list[dict[str, object]] = []
        for variant_index in range(1, 4):
            logger.info("route.generate.variant.start index=%s", variant_index)
            plan, planner_debug = await planner_service.plan_generate(
                prompt=payload.prompt,
                brand_constraints=payload.brandConstraints.model_dump(),
                variant_index=variant_index,
            )
            logger.info("route.generate.variant.plan index=%s plan=%s", variant_index, compact_json(plan, limit=2000))
            raw_svg, generator_debug = await svg_generation_service.generate_svg(plan=plan, original_svg=None)
            cleaned_svg = SVGValidator.strip_markdown_fences(raw_svg)
            normalized = SVGNormalizer.normalize(
                cleaned_svg,
                fallback_grid=payload.brandConstraints.grid,
                strip_transforms=False,
            )
            SVGValidator.validate_svg(normalized)
            logger.info("route.generate.variant.normalized index=%s svg=%s", variant_index, truncate_text(normalized, limit=2000))
            variants.append(Variant(svg=normalized))
            if debug_enabled:
                debug_variants.append(
                    {
                        "variantIndex": variant_index,
                        "planner": planner_debug,
                        "generator": generator_debug,
                        "normalizedSvg": normalized,
                    }
                )

        logger.info("route.generate.success variants=%s", len(variants))
        debug_payload: dict[str, object] | None = None
        if debug_enabled:
            debug_payload = {
                "provider": llm_meta["provider"],
                "model": llm_meta["model"],
                "variants": debug_variants,
            }

        return GenerateResponse(variants=variants, debug=debug_payload)
    except Exception as exc:
        logger.exception("route.generate.failed error=%s", exc)
        raise HTTPException(status_code=400, detail=f"generate_failed: {exc}") from exc
