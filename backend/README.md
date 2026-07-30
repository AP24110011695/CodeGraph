# CodeGraph Backend

Backend API for **CodeGraph** — The AI Software Architect for Every Codebase.

**Version:** `1.0.0-rc.1` (Release Candidate 1)

## Tech Stack

- **Python**: 3.12+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic v2
- **Settings**: pydantic-settings (`.env`)
- **Testing**: pytest

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/                 # Thin HTTP routers (registered in main.py)
│   ├── core/                # Settings + shared path helpers
│   ├── schemas/             # Pydantic request/response models
│   ├── parsers/             # Language parsing
│   ├── analyzers/           # Architecture builders
│   ├── services/            # Scanner, graphs, detectors
│   ├── quality|smells|refactoring|security|…
│   ├── repository_memory|semantic|rag|architecture_reasoning
│   ├── planning|agents|timeline|impact_analysis|engineering_reports
│   ├── copilot/             # Unified Intelligence Orchestrator (CG-070)
│   ├── cache|telemetry|workflows|workers|reliability|…
│   └── main.py              # FastAPI app, lifespan, middleware
├── tests/                   # pytest suite
├── requirements.txt
├── .env.example
└── README.md
```

See [`../AI_CONTEXT/MODULE_INDEX.md`](../AI_CONTEXT/MODULE_INDEX.md) for the full subsystem catalog.

## Core Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | App name, version, RC tag |
| GET | `/health` | Liveness + version + environment |
| POST | `/copilot/chat` | Unified intelligence Q&A |
| POST | `/copilot/execute` | Explicit tool orchestration |
| GET/DELETE | `/copilot/history` | Conversation memory |
| POST | `/quality/{upload_id}` | Quality analysis |
| POST | `/smells/{upload_id}` | Smell detection |
| POST | `/refactoring/{upload_id}` | Refactoring suggestions |

Full interactive docs: `http://127.0.0.1:8000/docs`

## Development

```bash
pytest tests/ -q
pytest tests/ --cov=app --cov-report=html
```

## Configuration

Copy `.env.example`. Important keys:

- `APP_VERSION` — defaults to `1.0.0-rc.1`
- `EXPOSE_ERROR_DETAILS` — keep `false` outside local debugging
- Optional `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` for LLM providers

## Production notes (RC-1)

- In-memory cache / vector store / conversation memory (process-local)
- Integration clients (GitHub/Jira/CI/Slack) are mock demonstrations
- Timeline VCS providers are stubs; local metadata history is default
- Prefer Copilot `/chat` over legacy chat mocks for repository intelligence

Details: [`../AI_CONTEXT/TECH_DEBT.md`](../AI_CONTEXT/TECH_DEBT.md)
