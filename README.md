# Nodebased-SVG – Gemini version

Production-oriented MVP scaffold for a web-based **Node-Based SVG Icon Generator and Mutation Engine**.

This branch represents the **Gemini-based version** of the system, using a **two-step model**:

1. **Text → JSON (Planning)**: Convert natural language prompts into a structured icon plan (JSON)
2. **JSON → SVG (Generation)**: Render that structured plan into clean, valid SVG code

## Architecture Overview

- `svg-engine/` – FastAPI backend (generate + mutate)
  - `routes/` – API endpoints for icon generation and mutation
  - `services/` – Core business logic
    - `planner_service.py` – Uses Gemini to convert prompts into structured plans (JSON)
    - `svg_generation_service.py` – Converts plans into SVG code
    - `gemini_provider.py` – LLM integration with Google Gemini
    - `svg_validator.py` – Validates generated SVG
    - `svg_normalizer.py` – Normalizes and optimizes SVG
  - `schemas/` – Request/response data models
- `frontend/` – Next.js app for the node-based UI and prompt interface

## Current Issue – Why this version fails

**Problem**: The current **Gemini 1.5 response structure is not working for us**.

- The planner stage expects a **stable, well-defined JSON schema** from Gemini 1.5.
- In practice, Gemini 1.5 responses are **inconsistent in structure** (fields missing, nesting changes, extra/unexpected keys).
- Our JSON → SVG pipeline is **strict about the schema**, so these structural variations cause:
  - JSON parsing/validation failures, or
  - Incorrect or incomplete SVG generation.

Because of this, the **two-step pipeline (Text → JSON → SVG) is not reliably usable** with the current Gemini 1.5 output format, and this version should be treated as experimental / failing for production use.

