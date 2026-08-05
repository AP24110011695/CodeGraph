# API notes

After `uvicorn app.main:app`, open `/docs` for the full OpenAPI list.

Useful ones:

| Method | Path |
|--------|------|
| GET | `/health` |
| POST | `/upload` |
| POST | `/copilot/chat` |
| POST | `/impact/analyze/{repository_id}` |
| GET | `/timeline/{repository_id}` |
| POST | `/reports/generate/{repository_id}` |
| POST | `/agents/execute/{repository_id}` |
| POST | `/quality/{upload_id}` |
| POST | `/smells/{upload_id}` |
| POST | `/refactoring/{upload_id}` |

Repository files may live under `storage/extracted/` or `uploads/` depending on the path; newer routers use `app.core.paths.resolve_repository_path`.
