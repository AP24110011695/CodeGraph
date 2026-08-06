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
storage/      # SQLite persistence (repository/index metadata)
tests/
```

Repository index metadata and extraction paths are persisted in SQLite
(`storage/codegraph.db` by default, override with `CODEGRAPH_DB_PATH`).
Extracted source trees remain on disk under `storage/extracted/`.

When using `--reload`, exclude extract/upload trees so WatchFiles does not
restart the server on every upload:

```bash
uvicorn app.main:app --reload --reload-exclude storage --reload-exclude uploads --port 8000
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

Known gaps (auth, Redis, live git, etc.): `../archive/TECH_DEBT.md`
