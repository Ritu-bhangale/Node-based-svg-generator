import asyncio
import logging
import time

from fastapi import APIRouter, HTTPException

from schemas.generate_schema import GenerateRequest, GenerateResponse
from services.starvector_service import starvector_service
from services.svg_normalizer import SVGNormalizer
from services.svg_validator import SVGValidator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=GenerateResponse)
async def generate_icon(payload: GenerateRequest) -> GenerateResponse:
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt must be a non-empty string")

    start = time.perf_counter()
    try:
        try:
            raw_svg = await asyncio.wait_for(starvector_service.generate(prompt), timeout=60.0)
        except asyncio.TimeoutError as exc:
            logger.error("route.generate.timeout prompt_len=%s", len(prompt))
            raise HTTPException(status_code=500, detail="SVG generation timed out") from exc

        cleaned_svg = SVGValidator.strip_markdown_fences(raw_svg)
        normalized_svg = SVGNormalizer.normalize(cleaned_svg, strip_transforms=False)
        SVGValidator.validate_svg(normalized_svg)

        elapsed = time.perf_counter() - start
        logger.info("route.generate.success prompt_len=%s elapsed=%.2fs", len(prompt), elapsed)
        return GenerateResponse(svg=normalized_svg)
    except MemoryError as exc:
        logger.exception("route.generate.oom error=%s", exc)
        raise HTTPException(status_code=500, detail="Out of memory during SVG generation") from exc
    except Exception as exc:
        logger.exception("route.generate.failed error=%s", exc)
        raise HTTPException(status_code=500, detail=f"generate_failed: {exc}") from exc

