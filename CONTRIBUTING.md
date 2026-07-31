# Contributing to CodeGraph

Thanks for your interest in contributing. CodeGraph is an **Enterprise AI Software Architecture Platform**. Contributions should strengthen architectural intelligence — not reinvent existing engines.

## Before you start

1. Read [`AI_CONTEXT/README_AI.md`](./AI_CONTEXT/README_AI.md)
2. Follow [`AI_CONTEXT/AI_RULES.md`](./AI_CONTEXT/AI_RULES.md)
3. Inspect `backend/app/main.py` and the target domain package
4. Prefer **composition** of existing engines over new parallel logic

## Development setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run tests from `backend/`:

```bash
python -m pytest tests/ -q
```

## Pull request checklist

- [ ] Reuses existing engines (no duplicate indexing / traversal / retrieval / business logic)
- [ ] Thin API router + Pydantic schemas when exposing HTTP
- [ ] Router registered in `app/main.py`
- [ ] Focused tests under `backend/tests/`
- [ ] Full suite still green
- [ ] AI_CONTEXT living docs updated when behavior/architecture changes
- [ ] No secrets committed (`.env`, API keys)

## Code style

- Package-per-capability under `backend/app/<name>/`
- Facade `*_engine.py` + module singleton
- Optional DI constructors defaulting to shared singletons
- Logging via `logging.getLogger(__name__)`
- Telemetry via `telemetry_manager` for significant work

## What we will not merge

- Second implementations of risk scoring, graph BFS, indexing, or memory stores
- Silent skips of failing tests without documented debt
- Provider-specific logic baked into Copilot/orchestration cores

## Questions

Open a GitHub issue with context, reproduction steps, and links to relevant `AI_CONTEXT` docs.
