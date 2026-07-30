# CodeGraph

**The AI Software Architect for Every Codebase**

**Release:** `1.0.0-rc.1` (Release Candidate 1)

---

## Vision

CodeGraph is an enterprise AI software architecture platform that analyzes repositories, builds knowledge graphs, maintains repository memory, plans multi-agent work, and answers engineering questions through a unified Copilot orchestrator.

It is **not** merely a code-search toy. See [`AI_CONTEXT/PROJECT_VISION.md`](./AI_CONTEXT/PROJECT_VISION.md).

---

## AI Assistants

**Start here:** [`AI_CONTEXT/README_AI.md`](./AI_CONTEXT/README_AI.md)

The `AI_CONTEXT/` folder is the permanent knowledge base for Cursor and other AI assistants (architecture, rules, roadmap, status, debt, module index).

---

## Current Status

**Release Candidate 1 (RC-1)** — backend intelligence platform is feature-complete for the CG-001…CG-070 stack with a green regression suite.

Authoritative live status: [`AI_CONTEXT/CURRENT_STATUS.md`](./AI_CONTEXT/CURRENT_STATUS.md)

---

## Capabilities (implemented)

- Repository upload, scan, parse, index (including incremental snapshots)
- Dependency / knowledge graphs and architecture analysis
- Quality, smells, refactoring, security, metrics, risk
- Repository Memory, Semantic Engine, Advanced RAG, Architecture Reasoning
- Planning Engine + Multi-Agent Framework
- Timeline Intelligence, Impact Analysis, Engineering Reports
- Unified Copilot Orchestrator (`/copilot/chat`, `/execute`, `/history`)
- Cache, Telemetry, Workflows, Workers, Reliability

---

## Repository Structure

```
CodeGraph/
├── AI_CONTEXT/           # Authoritative AI / engineering knowledge base
├── backend/
│   ├── app/
│   │   ├── api/          # Thin FastAPI routers
│   │   ├── core/         # Settings, shared paths
│   │   ├── schemas/      # Pydantic contracts
│   │   ├── <domain>/     # Engines (memory, rag, planning, agents, …)
│   │   └── main.py       # App entry + router registration
│   ├── tests/            # pytest suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/             # Client UI (separate tree; parity not required for RC-1)
└── README.md
```

---

## Quick Start (Backend)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: `GET http://127.0.0.1:8000/health`
- OpenAPI: `http://127.0.0.1:8000/docs`

```bash
pytest tests/ -q
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Tests | pytest |
| Cache | `CacheInterface` (in-memory; Redis-ready) |
| LLM | Provider ABC (OpenAI/Claude/Gemini + local heuristic) |

Production PostgreSQL/Celery/Redis/vector DB remain optional migrations — see [`AI_CONTEXT/TECH_DEBT.md`](./AI_CONTEXT/TECH_DEBT.md).

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [`AI_CONTEXT/ARCHITECTURE.md`](./AI_CONTEXT/ARCHITECTURE.md) | Implemented architecture |
| [`AI_CONTEXT/ROADMAP.md`](./AI_CONTEXT/ROADMAP.md) | Phases & milestones |
| [`AI_CONTEXT/MODULE_INDEX.md`](./AI_CONTEXT/MODULE_INDEX.md) | Subsystem catalog |
| [`AI_CONTEXT/TECH_DEBT.md`](./AI_CONTEXT/TECH_DEBT.md) | Known debt & stubs |
| [`backend/README.md`](./backend/README.md) | Backend developer guide |

---

## Contributing

Contributions are welcome. Prefer small PRs that reuse existing engines and follow [`AI_CONTEXT/AI_RULES.md`](./AI_CONTEXT/AI_RULES.md).

---

## License

MIT — see [LICENSE](LICENSE) when present.
