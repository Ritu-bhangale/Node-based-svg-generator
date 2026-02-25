import json
import logging
import os
from abc import ABC, abstractmethod

import httpx

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        raise NotImplementedError


class APIBasedLLMProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class MockLLMProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if "SVG planning engine" in system_prompt:
            payload = json.loads(user_prompt)
            mode = payload.get("mode", "generate")
            if mode == "mutate":
                return json.dumps(
                    {
                        "mode": "mutate",
                        "description": "Mock structural mutation plan",
                        "elements": [{"type": "path", "position": "center"}],
                        "style": {"grid": 24, "strokeWidth": 2, "outline": True},
                        "mutationIntent": "replaceShape",
                        "target": "circle",
                        "replacement": "heart",
                    }
                )

            variant = payload.get("variantIndex", 1)
            return json.dumps(
                {
                    "mode": "generate",
                    "description": f"Mock generated plan variant {variant}",
                    "elements": [{"type": "path", "position": "center"}],
                    "style": {
                        "grid": payload.get("brandConstraints", {}).get("grid", 24),
                        "strokeWidth": payload.get("brandConstraints", {}).get("strokeWidth", 2),
                        "outline": payload.get("brandConstraints", {}).get("style", "outline") == "outline",
                    },
                }
            )

        if "SVG generation engine" in system_prompt:
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.2A4 4 0 0 1 19 11c0 5.65-7 10-7 10Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>'

        return "{}"


def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if not provider:
        if os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.getenv("LLM_API_KEY"):
            provider = "api"
        else:
            provider = "mock"

    if provider == "gemini":
        from services.gemini_provider import GeminiProvider

        return GeminiProvider()

    if provider == "api":
        return APIBasedLLMProvider(
            base_url=os.getenv("LLM_API_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        )
    logger.info(f"LLM Provider = {provider}")
    return MockLLMProvider()


def get_llm_metadata() -> dict[str, str]:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if not provider:
        if os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.getenv("LLM_API_KEY"):
            provider = "api"
        else:
            provider = "mock"
    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    elif provider == "api":
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    else:
        model = "mock"
    return {"provider": provider, "model": model}
