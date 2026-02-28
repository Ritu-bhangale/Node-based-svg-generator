from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., max_length=500, description="Natural language description of the desired SVG icon.")


class GenerateResponse(BaseModel):
    svg: str = Field(..., description="Cleaned, validated SVG output.")

