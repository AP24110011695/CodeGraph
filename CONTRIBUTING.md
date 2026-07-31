# Contributing

Thanks for contributing to CodeGraph.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
python -m pytest tests/ -q
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
npm run lint
npm run build
```

Local frontend expects the API via `VITE_API_URL=/api` (Vite proxies to `127.0.0.1:8000`).

## Guidelines

### Backend

- Put domain logic in `backend/app/<domain>/`, not in routers.
- Reuse existing engines (indexing, graph traversal, memory, scoring) instead of copying them.
- If you add an API module, register it in `app/main.py`.
- Add or update tests under `backend/tests/`.

### Frontend

- Follow `FRONTEND_ARCHITECTURE.md`.
- Keep feature folders as `features/<name>/{api,components,hooks,store?,index.ts}`.
- Use TanStack Query for server data and Zustand only for UI/client state.
- Do not invent fake APIs or change backend contracts from the frontend.

### General

- Don’t commit secrets (`.env`, API keys).
- Prefer focused pull requests.
- Note intentional debt in `AI_CONTEXT/TECH_DEBT.md` when relevant.

Internal architecture notes live in `AI_CONTEXT/` (for contributors and coding agents). Start with `AI_CONTEXT/README_AI.md` if you are changing engines.

## Pull requests

1. Keep changes focused.
2. Include a short summary and test plan.
3. Run backend tests and/or `npm run lint` + `npm run build` for frontend changes.
