# Nodebased-SVG MVP

Production-oriented MVP scaffold for a web-based Node-Based SVG Icon Generator and Mutation Engine.

## Architecture Overview

This project implements a **two-stage AI-powered SVG generation pipeline**:

1. **Planning Stage (Text → JSON)**: Convert natural language prompts into structured icon plans
2. **Generation Stage (JSON → SVG)**: Render structured plans into clean SVG code

## Structure

- `svg-engine/`: FastAPI backend (generate + mutate)
  - `routes/`: API endpoints for icon generation and mutation
  - `services/`: Core business logic
    - `planner_service.py`: Converts prompts to structured plans (JSON)
    - `svg_generation_service.py`: Converts plans to SVG code
    - `gemini_provider.py`: LLM integration with Google Gemini
    - `svg_validator.py`: Validates generated SVG
    - `svg_normalizer.py`: Normalizes and optimizes SVG
  - `schemas/`: Request/response data models
- `frontend/`: Next.js App Rout# Nodebased-SVG MVP

Production-oriented MVP scaffold for a web-baseh

Production-oriethon3
## Architecture Overview

This project implements a **two-stage AI-powered SVG generation pipelinari
This project implementMIN
1. **Planning Stage (Text → JSON)**: Convert natural language prompts ierv2. **Generation Stage (JSON → SVG)**: Render structured plans into clean SVG code

## Structureal
## Structure

- `svg-engine/`: FastAPI backend (generate + mutate)
  - `routes/`:xam
- `svg-engKno  - `routes/`: API endpoints for icon generation anta  - `services/`: Core business logic
    - `planner_service.it    - `planner_service.py`: Convert?   - `svg_generation_service.py`: Converts issue:

**Problem**: Gemini     - `gemini_provider.py`: LLM integration with Google Gemica    - `svg_validator.py`: Validates generated SVG
    - `svg_ i    - `svg_normalizer.py`: Normalizes and optimiti  - `schemas/`: Request/response data models
- `fr192`
 - `frontend/`: Next.js App Rout# Nodebased-ni
Production-oriented MVP scaffold for a web-basehtio
Production-oriethon3
## Architecture Overview
n m## Architecture Ovehy
This project implement1.5This project implementMIN
1. **Planning Stage (Text → JSON)**: Convert ng1. **Planning Stage (Tex i
## Structureal
## Structure

- `svg-engine/`: FastAPI backend (generate + mutate)
  - `routes/`:xam
- `svg-engKno  - `routes/`: API endpoints for icon generaunc## Structure
le
- `svg-eng# W  - `routes/`:xam
- `svg-engKno  - `routes/`: API eke- `svg-engKno  - 8    - `planner_service.it    - `planner_service.py`: Convert?   - `svg_generation_service.py`: Convro
**Problem**: Gemini     - `gemini_provider.py`: LLM integration with Google Gemica    - `svg_validator.py`: Va Im    - `svg_ i    - `svg_normalizer.py`: Normalizes and optimiti  - `schemas/`: Request/response data models
- `fr192`
 - `frontendti- `fr192`
 - `frontend/`: Next.js App Rout# Nodebased-ni
Production-oriented MVP scaffold for a web-bT http: - `fronosProduction-oriented MVP scaffold for a web-batiProduction-oriethon3
## Architecture Overview
n m#fu## Architecture Ove "n m## Architecture Oveh  This project implement1ro1. **Planning Stage (Text → JSON)**: Convert ng'
## Structureal
## Structure

- `svg-engine/`: FastAPI backend (generate + DM## Structure
vg
- `svg-engnd   - `routes/`:xam
- `svg-engKno  - `routes/`e.
