import json
from typing import Any


def truncate_text(value: str, limit: int = 1500) -> str:
    text = value if isinstance(value, str) else str(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def compact_json(value: Any, limit: int = 1500) -> str:
    try:
        rendered = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        rendered = str(value)
    return truncate_text(rendered, limit=limit)
