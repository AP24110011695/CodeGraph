# Project Architecture

Short map of how CodeGraph fits together for contributors and reviewers.

## System layers

```text
┌──────────────────────────────────────────────┐
│ Frontend (Vite + React + TypeScript)         │
│  features/* → TanStack Query → Axios client  │
└──────────────────────┬───────────────────────┘
                       │ /api (local Vite proxy)
┌──────────────────────▼───────────────────────┐
│ FastAPI routers (backend/app/api)            │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│ Analysis engines (backend/app/<domain>)      │
│ upload, indexing, graphs, quality, security, │
│ metrics, timeline, impact, architecture, …   │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│ AI intelligence modules                      │
│ copilot, RAG, repository memory, planning,   │
│ agents, engineering reports                  │
└──────────────────────────────────────────────┘
```

## Frontend shape

- `src/app` — router, providers, suspense fallbacks
- `src/features/<feature>` — API types/adapters/queries + UI panels
- `src/design-system` — shared primitives (Button, Badge, Toast, …)
- `src/pages` — thin route wrappers
- `src/core` — API client, stores, auth/route guards

Official blueprint: [`FRONTEND_ARCHITECTURE.md`](../FRONTEND_ARCHITECTURE.md)

## Backend shape

- `backend/app/api` — thin HTTP routers
- `backend/app/<domain>` — engines / analyzers
- `backend/app/schemas` — Pydantic response models
- `backend/tests` — pytest coverage

Short backend overview: [`architecture/OVERVIEW.md`](./architecture/OVERVIEW.md)

## Data flow example

1. User uploads a ZIP (`POST /upload`)
2. Frontend starts indexing (`POST /index/{id}`) and polls repository state
3. Dashboard loads overview adapters (frameworks, architecture summary, quality/risk)
4. Feature pages call their domain endpoints and adapt responses for React Flow / Recharts / markdown viewers

## Local networking note

Backend currently has no CORS middleware for browser-origin calls. Local frontend therefore uses:

```env
VITE_API_URL=/api
```

and Vite proxies `/api` → `http://127.0.0.1:8000`.

## Known architectural constraints

- Some endpoints depend on process-local in-memory indexes
- Copilot chat is request/response JSON (streaming not fully wired)
- Deployment / auth / durable stores are outside RC-1 scope
