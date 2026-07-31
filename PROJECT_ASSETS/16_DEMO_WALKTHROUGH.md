# Demo Walkthrough

## Prep (2 minutes)

```bash
cd backend
source .venv/bin/activate  # or Windows equivalent
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs

## Flow

1. **Health** — `GET /health` shows `1.0.0-rc.1`.  
2. **Upload** — upload a small sample zip via `/upload` (or use an existing `uploads/` demo repo id).  
3. **Memory** — build/fetch repository memory.  
4. **Copilot** — `POST /copilot/chat` with `{ "repository_id": "...", "query": "Explain the architecture", "provider": "local" }`.  
5. **Impact** — `POST /impact/analyze/{id}` with a target symbol/module.  
6. **Timeline** — `GET /timeline/{id}` or hotspots.  
7. **Report** — `POST /reports/generate/{id}`.  
8. **Show tests** — `pytest tests/ -q` green headline.

Narrate composition: Copilot did not re-analyze from scratch—it orchestrated engines.
