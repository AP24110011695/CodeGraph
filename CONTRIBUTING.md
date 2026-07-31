# Contributing

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
python -m pytest tests/ -q
```

## Guidelines

- Put domain logic in `backend/app/<domain>/`, not in routers.
- Reuse existing engines (indexing, graph traversal, memory, scoring) instead of copying them.
- If you add an API module, register it in `app/main.py`.
- Add or update tests under `backend/tests/`.
- Don’t commit secrets (`.env`, API keys).

Internal architecture notes live in `AI_CONTEXT/` (for contributors and coding agents). Start with `AI_CONTEXT/README_AI.md` if you are changing engines.

## Pull requests

Keep changes focused. Note any new debt in `AI_CONTEXT/TECH_DEBT.md` when you intentionally leave something stubbed.
