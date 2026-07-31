# CodeGraph

[![CI](https://github.com/AP24110011695/CodeGraph/actions/workflows/ci.yml/badge.svg)](https://github.com/AP24110011695/CodeGraph/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](./backend/requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

AI-assisted repository intelligence platform. Upload a codebase, index it, and explore structure, quality, architecture, and change impact through a FastAPI analysis backend and a React dashboard.

**Version:** `1.0.0-rc.1`

## Project overview

CodeGraph helps engineers understand unfamiliar repositories faster.

**Problem:** Large codebases make architecture, risk, and impact hard to see without weeks of tribal knowledge.

**Solution:** CodeGraph runs a repository analysis pipeline, then surfaces results in interactive views — dependency graphs, AI copilot answers, semantic search, reports, timeline evolution, and quality/security/metrics dashboards.

### Key capabilities

- Upload and index a repository ZIP
- Visualize dependency and architecture relationships
- Ask repository questions via Copilot
- Search code semantically
- Generate engineering reports
- Explore quality, security, metrics, and change impact

## Features

| Area | What you get |
|------|----------------|
| Repository analysis | Upload → extract → index → dashboard overview |
| Dependency Graph | Interactive React Flow graph of internal dependencies |
| AI Copilot | Orchestrated Q&A over repository engines (`POST /copilot/chat`) |
| Semantic Search | Hybrid/semantic/keyword search with code preview |
| Architecture | Layered module diagram + explanation panel |
| Knowledge Graph | Semantic entity/relationship explorer |
| Reports | Generate and view markdown engineering reports |
| Timeline | Commit/evolution timeline, hotspots, snapshot compare |
| Quality | Scores, recommendations, code smells/hotspots |
| Security | Vulnerability list and severity summary |
| Metrics | Language breakdown and metric cards (Recharts) |
| Impact | Target a change and inspect predicted blast radius |

## Tech stack

### Frontend

- React 18 + TypeScript + Vite
- Tailwind CSS + CVA design-system primitives
- TanStack Query (server state)
- Zustand (UI/client state)
- React Router
- React Flow (`@xyflow/react`)
- Recharts
- Framer Motion
- Axios + react-markdown

### Backend

- FastAPI + Uvicorn + Pydantic v2
- Repository analysis pipeline (scan, parse, index, graphs)
- AI/ML and intelligence modules (copilot, RAG, memory, planning, agents)
- pytest suite

## Architecture overview

```text
Frontend (React dashboard)
        ↓  HTTP /api (Vite proxy in local dev)
FastAPI routers (backend/app/api)
        ↓
Analysis engines (backend/app/<domain>)
        ↓
AI intelligence modules (copilot, RAG, memory, planning, …)
```

Frontend feature modules call real backend routes through adapters. No fake APIs.

Details: [docs/PROJECT_ARCHITECTURE.md](./docs/PROJECT_ARCHITECTURE.md) · [docs/architecture/OVERVIEW.md](./docs/architecture/OVERVIEW.md) · [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)

## Project structure

```text
frontend/                 # React + Vite dashboard
  src/app/                # Router, providers
  src/features/           # Feature modules (upload, graph, copilot, …)
  src/design-system/      # Shared UI primitives
  src/pages/              # Route pages
backend/app/              # FastAPI app, engines, schemas
backend/tests/            # pytest suite
docs/                     # Architecture / API / project docs
FRONTEND_ARCHITECTURE.md  # Official frontend blueprint
AI_CONTEXT/               # Contributor / coding-agent notes
```

## Setup instructions

### Prerequisites

- Python 3.12+
- Node.js 20+ (recommended)
- Backend on `http://127.0.0.1:8000`

### Backend

```bash
cd backend
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

LLM API keys are optional. Copilot can use a local fallback provider.

More: [backend/README.md](./backend/README.md) · [backend/.env.example](./backend/.env.example)

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open http://127.0.0.1:5173

`VITE_API_URL=/api` uses the Vite proxy to the backend (no CORS setup required locally).

```bash
npm run build
npm run lint
```

Env template: [frontend/.env.example](./frontend/.env.example)

### Typical flow

Upload ZIP → Index → Dashboard → Graph → Copilot → Search → Reports → Timeline → Quality / Security / Metrics / Impact → Architecture → Knowledge Graph

## Current limitations

Documented honestly for local/demo use:

- Some analysis services rely on **in-memory IndexManager** instances; metrics / knowledge-graph / related endpoints may return 404/400 after indexing via API if the process memory does not hold a READY index
- Copilot uses **JSON responses today** (no SSE streaming UI wired end-to-end)
- **Mermaid** rendering is only meaningful when backend payloads include Mermaid content
- **No production deployment** packaging (auth, durable stores, Redis, vector DB, hosted CI/CD deploy) is included in this RC
- Security analysis currently resolves extracted paths under `storage/extracted/{id}`
- Treat RC-1 as a **local / single-tenant** tool; no built-in auth

## Screenshots

> Screenshots placeholder — add UI captures here for GitHub README polish:
>
> - Dashboard overview
> - Dependency graph
> - Copilot chat
> - Architecture / knowledge graph
> - Reports / timeline / analysis pages

## Future improvements

- Durable indexing and shared IndexManager lifecycle across API workers
- SSE/streaming Copilot responses
- Auth and multi-tenant workspace model
- Persistent vector store / Redis-backed cache
- Mermaid diagram rendering when backend returns diagram payloads
- Playwright E2E coverage for the full upload → analysis flow
- Production deploy docs (Docker / cloud)

## API (selected)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/upload` | Upload repository ZIP |
| POST/GET | `/index/{upload_id}` | Index repository |
| GET | `/dependency-graph/{upload_id}` | Dependency graph |
| POST | `/copilot/chat` | Orchestrated Q&A |
| POST | `/semantic/{upload_id}` | Semantic search |
| POST | `/reports/generate/{repository_id}` | Generate report |
| GET | `/timeline/{repository_id}` | Timeline intelligence |
| POST | `/quality/{upload_id}` | Quality analysis |
| POST | `/security/{upload_id}` | Security analysis |
| POST | `/metrics/{upload_id}` | Metrics |
| POST | `/impact/analyze/{repository_id}` | Change impact |
| GET | `/architecture/{upload_id}` | Architecture |
| POST | `/knowledge-graph/{upload_id}` | Knowledge graph |

Full list: OpenAPI at `/docs` or [docs/api/OVERVIEW.md](./docs/api/OVERVIEW.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Prefer reusing existing engines/features over adding parallel ones.

## Security

No built-in auth in RC-1. Put it behind your own access control before exposing it. [SECURITY.md](./SECURITY.md)

## License

[MIT](./LICENSE)
