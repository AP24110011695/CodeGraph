# CodeGraph

[![CI](https://github.com/AP24110011695/CodeGraph/actions/workflows/ci.yml/badge.svg)](https://github.com/AP24110011695/CodeGraph/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](./backend/requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

FastAPI backend that analyzes software repositories: structure, quality, architecture, and change impact. Includes repository memory, RAG, a planning/multi-agent layer, and a Copilot API that routes questions to those engines.

**Version:** `1.0.0-rc.1`

## Features

- Upload, scan, parse, and index repositories (including incremental snapshots)
- Dependency graph and knowledge graph
- Quality, smells, refactoring, security, metrics, and risk analysis
- Repository memory, semantic search, and RAG
- Architecture reasoning, planning, and multi-agent execution
- Timeline / evolution views and change-impact analysis
- Engineering reports and `POST /copilot/chat` orchestration
- Cache and telemetry facades, workflows, and workers

## Architecture

```text
Client → FastAPI routers → domain engines
                ↓
         Copilot (optional)
                ↓
    Planning → tools (memory, RAG, timeline, impact, agents, …)
```

Engines live under `backend/app/<domain>/`. Routers stay thin. Details: [docs/architecture/OVERVIEW.md](./docs/architecture/OVERVIEW.md).

## Quick start

```bash
git clone https://github.com/AP24110011695/CodeGraph.git
cd CodeGraph/backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

```bash
python -m pytest tests/ -q
```

Python 3.12+. LLM API keys are optional; Copilot can run with the local fallback provider.

More backend notes: [backend/README.md](./backend/README.md).

## Project structure

```text
backend/app/          # FastAPI app, engines, schemas
backend/tests/        # pytest suite
docs/                 # Short architecture / API notes
AI_CONTEXT/           # Internal notes for contributors & coding agents
PROJECT_ASSETS/       # Optional resume / interview notes
frontend/             # Vite + React scaffold (not the RC focus)
```

## API (selected)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/copilot/chat` | Orchestrated Q&A |
| POST | `/impact/analyze/{repository_id}` | Change impact |
| GET | `/timeline/{repository_id}` | Evolution / hotspots |
| POST | `/reports/generate/{repository_id}` | Composed report |
| POST | `/agents/execute/{repository_id}` | Multi-agent run |
| POST | `/quality/{upload_id}` | Quality analysis |

Full list: OpenAPI at `/docs` or [docs/api/OVERVIEW.md](./docs/api/OVERVIEW.md).

## Stack

FastAPI, Uvicorn, Pydantic v2, pytest, tree-sitter, in-memory cache (Redis-ready interface), pluggable LLM providers.

## Roadmap / status

RC-1 focuses on the backend intelligence stack. Still open for a production deploy: auth, durable stores, Redis, real VCS providers, and vector DB. See [CHANGELOG.md](./CHANGELOG.md) and [AI_CONTEXT/TECH_DEBT.md](./AI_CONTEXT/TECH_DEBT.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Prefer reusing existing engines over adding parallel ones. Register new routers in `backend/app/main.py`.

## Security

No built-in auth in RC-1. Treat as a local/single-tenant tool until you put it behind your own access control. [SECURITY.md](./SECURITY.md)

## License

[MIT](./LICENSE)
