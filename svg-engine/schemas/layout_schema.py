from typing import Any

from pydantic import BaseModel, Field


class BrandConstraints(BaseModel):
    grid: int = Field(default=24, ge=8, le=256)
    strokeWidth: float = Field(default=2.0, ge=0.1, le=32)
    style: str = Field(default="outline")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=500)
    brandConstraints: BrandConstraints


class Variant(BaseModel):
    svg: str


class GenerateResponse(BaseModel):
    variants: list[Variant]
    debug: dict[str, Any] | None = None
