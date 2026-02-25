from typing import Any

from pydantic import BaseModel, Field


class MutateRequest(BaseModel):
    svg: str = Field(min_length=11)
    userInput: str = Field(min_length=2, max_length=500)


class MutateResponse(BaseModel):
    svg: str
    debug: dict[str, Any] | None = None
