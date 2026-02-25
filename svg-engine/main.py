import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.generate import router as generate_router
from routes.mutate import router as mutate_router
from services.llm_provider import get_llm_metadata


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()

app = FastAPI(title="svg-engine", version="0.1.0")
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="", tags=["generate"])
app.include_router(mutate_router, prefix="", tags=["mutate"])


@app.on_event("startup")
async def on_startup() -> None:
    llm_meta = get_llm_metadata()
    logger.info("startup.llm provider=%s model=%s", llm_meta["provider"], llm_meta["model"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
