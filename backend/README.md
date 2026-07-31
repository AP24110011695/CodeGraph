# Backend

FastAPI service for CodeGraph (`1.0.0-rc.1`).

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Layout

```text
app/
  api/        # HTTP routers
  core/       # settings, path helpers
  schemas/    # Pydantic models
  <domain>/   # engines (memory, rag, planning, agents, …)
  main.py
tests/
```

## Useful endpoints

- `GET /health`
- `POST /copilot/chat`
- `POST /quality/{upload_id}`, `/smells/{upload_id}`, `/refactoring/{upload_id}`

Interactive docs: `/docs`

## Config

See `.env.example`. Keep `EXPOSE_ERROR_DETAILS=false` unless you are debugging locally.

## Tests

```bash
python -m pytest tests/ -q
```

Known gaps (auth, Redis, live git, etc.): `../AI_CONTEXT/TECH_DEBT.md`
