# API Overview (RC-1)

Interactive docs: `http://127.0.0.1:8000/docs` after starting the server.

## Platform

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Name, version, RC tag |
| GET | `/health` | Liveness |

## Intelligence (high-value)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/copilot/chat` | Unified AI Software Architect Q&A |
| POST | `/copilot/execute` | Explicit tool orchestration |
| GET/DELETE | `/copilot/history` | Conversation memory |
| POST | `/planning/plan/{repository_id}` | Intent → module plan |
| POST | `/agents/execute/{repository_id}` | Multi-agent collaboration |
| POST | `/impact/analyze/{repository_id}` | Change blast radius |
| GET | `/timeline/{repository_id}` | Repository evolution |
| POST | `/reports/generate/{repository_id}` | Composed engineering report |
| POST | `/rag/...` | Advanced RAG context |
| GET/POST | `/repository-memory/...` | Structured memory |

## Analysis

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/quality/{upload_id}` | Quality scores |
| POST | `/smells/{upload_id}` | Smell detection |
| POST | `/refactoring/{upload_id}` | Refactor suggestions |
| GET | `/architecture/{upload_id}` | Architecture model |
| POST | `/architecture/explain/{repository_id}` | Architecture reasoning |
| POST | `/security/{upload_id}` | Security analysis |
| POST | `/risk/{upload_id}` | Risk scoring |

## Ingest

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/upload` | Upload repository archive |
| POST | `/scan/{upload_id}` | Inventory files/languages |
| POST | `/index/{upload_id}` | Build search index |

Full catalog: OpenAPI `/openapi.json` and [`AI_CONTEXT/MODULE_INDEX.md`](../AI_CONTEXT/MODULE_INDEX.md).
