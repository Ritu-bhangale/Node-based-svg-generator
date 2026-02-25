# svg-engine

FastAPI backend for two-stage LLM-driven SVG generation and mutation.

## Run

```bash
cd svg-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Endpoints

- `POST /generate`
- `POST /mutate`
- `GET /health`
