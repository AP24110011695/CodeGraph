# Demo notes

```bash
cd backend
source .venv/bin/activate   # or Windows equivalent
uvicorn app.main:app --reload --port 8000
```

1. Open http://127.0.0.1:8000/docs  
2. `GET /health` — confirm version  
3. Upload a small repo (`/upload`) or use an existing upload id  
4. `POST /copilot/chat` with a question like “Explain the architecture” (`provider: local` is fine)  
5. Optionally `POST /impact/analyze/{id}` and `GET /timeline/{id}`  
6. Show `pytest tests/ -q` if you want proof of the suite  

Keep the story short: Copilot calls existing engines; it doesn’t re-scan the world from scratch.
