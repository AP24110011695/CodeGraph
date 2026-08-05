# BACKEND_REBUILD_MASTER_PLAN.md

> CodeGraph Backend — Engineering Execution Manual  
> Status: ACTIVE | Version: 1.0  
> Rule: Update this file after completing every phase. Never skip a phase. Never begin the next phase until Exit Criteria are satisfied.

---

## FINAL DEFINITION OF DONE

The backend rebuild is complete **only** when every item below is checked:

- [ ] FastAPI starts with zero errors
- [ ] Swagger UI loads at `/docs`
- [ ] Every endpoint is listed in Swagger
- [ ] Every endpoint executes without crashing
- [ ] Every endpoint returns real data derived from an actual uploaded repository
- [ ] No endpoint returns placeholder, hardcoded, or dummy data
- [ ] Repository upload works end-to-end
- [ ] ZIP extraction works correctly
- [ ] Repository scanning produces real file trees
- [ ] AST parsing produces real symbol data
- [ ] Indexing produces real embeddings stored in the vector store
- [ ] Repository Memory APIs return real per-repository context
- [ ] RAG retrieval returns real grounded results
- [ ] Dashboard APIs return real analysis data
- [ ] Copilot APIs return real AI-generated responses
- [ ] All error responses follow a consistent schema
- [ ] No 500 errors on valid input
- [ ] Background jobs complete without hanging
- [ ] Final Swagger validation checklist — all endpoints marked PASS

---

## PHASE 0 — Repository Sanity Check

### Objective

Establish a verified, clean starting point before touching any code.

### Why This Phase Exists

You cannot debug a system you do not understand. This phase ensures the codebase is in a known state before any repair work begins.

### Files to Inspect

- `README.md` — understand intended startup procedure
- `pyproject.toml` or `requirements.txt` or `requirements-dev.txt` — dependency inventory
- `app/main.py` — entry point
- `.env.example` or `.env.template` — required environment variables
- `alembic.ini` or `migrations/` — database migration state
- `docker-compose.yml` — external service dependencies
- `app/core/config.py` — configuration model
- `app/api/router.py` or equivalent — top-level router registration

### APIs Involved

None — this is inspection only.

### Swagger Endpoints to Verify

None yet.

### Expected Request

N/A

### Expected Response

N/A

### Success Criteria

- You can describe the full dependency graph of the project in one paragraph
- You know every external service the backend requires (PostgreSQL, Redis, S3, vector DB, etc.)
- You know every environment variable that must be set
- You know the exact command to start the backend
- You have identified every file that currently contains `TODO`, `pass`, `raise NotImplementedError`, `return {}`, or hardcoded dummy values

### Manual Verification Steps

1. Clone or open the repository in your IDE
2. Run: `grep -rn "TODO\|NotImplementedError\|dummy\|placeholder\|return {}\|mock" app/ --include="*.py"` — record every result
3. Run: `grep -rn "raise NotImplementedError" app/ --include="*.py"` — these are guaranteed failures
4. Open `app/main.py` — list every router that is registered
5. Open `app/core/config.py` — list every required setting
6. Open `.env.example` — verify every variable has a description
7. Run: `pip install -r requirements.txt` in a clean virtual environment — record any installation errors
8. Attempt cold start: `uvicorn app.main:app --reload` — record every error

### Automated Tests

```bash
# Count unimplemented endpoints
grep -rn "NotImplementedError\|pass$\|return {}" app/ --include="*.py" | wc -l

# List all route decorators
grep -rn "@router\.\|@app\." app/ --include="*.py"

# Check import errors
python -c "import app.main" 2>&1
```

### Common Failure Points

- Missing `__init__.py` in subpackages causing import failures
- Circular imports between modules
- Environment variables referenced before config is loaded
- Database models imported at top level causing startup failures
- Missing dependency in `requirements.txt` that exists only in a developer's local environment

### Debugging Checklist

- [x] Can you import `app.main` with zero errors?
- [x] Is every file in `app/api/` reachable via the router?
- [x] Does every model in `app/models/` have a corresponding migration?
- [x] Does every service in `app/services/` have its dependencies injected — not globally instantiated?
- [x] Is there a circular import? Run: `python -c "from app.main import app"` and read the full traceback

### Exit Criteria

- [x] Complete map of all unimplemented endpoints documented
- [x] All external dependencies identified
- [x] All required environment variables listed
- [x] Cold start attempt completed and all errors recorded
- [x] No ambiguity about what the project is supposed to do

### Git Commit Suggestion

```
chore: phase 0 complete — repository audit, all gaps documented
```

### Completion Checklist

- [x] Unimplemented endpoint list written
- [x] External service list written
- [x] Required `.env` variables listed
- [x] Cold start errors recorded
- [x] Phase 0 row updated in this document

### Phase 0 Audit Record (2026-08-05)

#### What the project is supposed to do

CodeGraph is an AI-assisted repository intelligence platform. Users upload a codebase ZIP; the FastAPI backend extracts, scans, parses (AST/tree-sitter), indexes (embeddings + local vector store), builds repository memory, and exposes dashboard / RAG / Copilot APIs over that real analysis. Persistence is local SQLite + filesystem (no Postgres/Redis/S3 required for RC-1).

#### Startup command (exact)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# Prefer excluding storage/uploads under --reload:
# uvicorn app.main:app --reload --reload-exclude storage --reload-exclude uploads --host 127.0.0.1 --port 8000
```

Docs: `http://127.0.0.1:8000/docs` · Health: `http://127.0.0.1:8000/health`

#### Dependency graph (one paragraph)

The backend is a FastAPI (`0.115`) + Uvicorn app using Pydantic v2 / pydantic-settings for config, SQLAlchemy 2 + Alembic (packaged but **no `alembic.ini` / migrations tree present**) for SQLite ORM persistence under `storage/`, python-multipart + aiofiles for ZIP upload/IO, tree-sitter (+ Python/JS/TS grammars) for AST parsing, sentence-transformers (+ torch/numpy) for local embeddings written under `storage/vectors/`, and optional Groq (httpx) for LLM chat when `GROQ_API_KEY` is set; pytest/httpx support the test suite. There is **no** `docker-compose.yml`, no PostgreSQL, no Redis, and no S3 — external services are optional LLM HTTP APIs only; everything else is in-process / on-disk.

#### External services / dependencies

| Dependency | Required? | Notes |
| ---------- | --------- | ----- |
| Local filesystem (`uploads/`, `storage/`, `storage/extracted/`, `storage/vectors/`) | Yes | Upload, extract, SQLite, vectors |
| SQLite (`CODEGRAPH_DB_PATH`, default `storage/codegraph.db`) | Yes | Created on startup via `storage.database.init_db()` |
| Hugging Face / local sentence-transformers model download | Soft | First embedding run may download model weights |
| Groq API | Optional | Copilot/LLM when key set |
| OpenAI / Anthropic / Gemini APIs | Optional | Declared in settings; unused unless provider selected |
| PostgreSQL | No | Not used |
| Redis | No | Not used (in-process job/worker/cache) |
| S3 / object storage | No | Not used |
| Docker Compose | Absent | No `docker-compose.yml` in repo |
| Alembic migrations | Absent | `alembic` in requirements; schema via `init_db` / column patches |

#### Required environment variables (`app/core/config.py` ↔ `.env.example`)

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `APP_NAME` | No (default `CodeGraph`) | Application name |
| `APP_VERSION` | No (default `1.0.0-rc.1`) | Version string |
| `HOST` | No (default `127.0.0.1`) | Bind host |
| `PORT` | No (default `8000`) | Bind port |
| `EXPOSE_ERROR_DETAILS` | No (default `true` in code / example) | Include exception text on HTTP 500 |
| `UPLOAD_DIR` | No (default `uploads`) | Upload directory |
| `STORAGE_DIR` | No (default `storage`) | Storage root |
| `CODEGRAPH_DB_PATH` | No (default `storage/codegraph.db`) | SQLite path |
| `VECTOR_STORAGE_PATH` | No (default `storage/vectors`) | Vector store path |
| `OPENAI_API_KEY` | Optional | OpenAI |
| `ANTHROPIC_API_KEY` | Optional | Anthropic |
| `GEMINI_API_KEY` | Optional | Gemini |
| `GROQ_API_KEY` | Optional | Groq |
| `GROQ_MODEL` | No (default `llama-3.3-70b-versatile`) | Groq model |

**Config gap (record only — do not fix in Phase 0):** `Settings.model_config` loads `env_file` from repo root (`Path(__file__).parents[3] / ".env"`), while `.env.example` / local `.env` live under `backend/`. Cold start used defaults successfully; `backend/.env` may not be applied until Phase 2/3.

**Stray `os.getenv`:** `app/ai/llm_client.py` reads `GROQ_API_KEY` outside `config.py`; `storage/database.py` also checks `CODEGRAPH_DB_PATH` via `os.environ`.

#### Routers registered in `app/main.py` (64 include_router calls + `/` + `/health`)

`upload`, `repositories`, `scanner`, `framework`, `dependency_graph`, `parser`, `architecture_reasoning`, `architecture`, `diagrams`, `explain`, `chat`, `indexing`, `readme`, `search`, `apidocs`, `uml`, `security`, `quality`, `smells`, `refactoring`, `metrics`, `review`, `knowledge_graph`, `risk`, `dependency_health`, `license`, `architecture_drift`, `architecture_recommendation`, `bug_localization`, `pull_request_review`, `code_generation`, `design_patterns`, `solid`, `microservices`, `database_schema`, `api_flow`, `architecture_report`, `workspace`, `github`, `cicd`, `jira`, `notifications`, `team_analytics`, `repository_comparison`, `release_notes`, `dashboard`, `copilot`, `jobs`, `repository_state`, `events`, `workflows`, `workers`, `reliability`, `incremental_indexing`, `cache`, `telemetry`, `semantic`, `repository_memory`, `rag`, `planning`, `agents`, `timeline`, `impact_analysis`, `engineering_reports`.

Cold-start OpenAPI path count: **121** unique paths (including `/docs`, `/openapi.json`, `/redoc`).

#### Unimplemented / mock / stub map

**`raise NotImplementedError` (guaranteed failures if invoked):**

| Location | What fails |
| -------- | ---------- |
| `app/timeline/history_provider.py` | `GitHistoryProvider`, `GitHubHistoryProvider`, `GitLabHistoryProvider`, `BitbucketHistoryProvider` |
| `app/engineering_reports/exporters.py` | `HtmlReportExporter`, `PdfReportExporter` |
| `app/api/engineering_reports.py` | Catches `NotImplementedError` from exporters |

**Documented mock integrations (return fake/demo data):**

| Area | File | Affects APIs |
| ---- | ---- | ------------ |
| GitHub | `app/github/github_client.py` | `/github/*` |
| Jira | `app/jira/jira_client.py` | `/jira/*` |
| CI/CD | `app/cicd/provider_client.py` | `/cicd/*` |
| Slack | `app/notifications/slack_client.py` | `/notifications/slack` |
| Discord | `app/notifications/discord_client.py` | `/notifications/discord` |
| Chat LLM | `app/chat/chat_service.py` | `/chat/*` (mock answers) |

**Other stub / placeholder signals:**

| Location | Signal |
| -------- | ------ |
| `app/code_generation/template_selector.py` | Many `# TODO` placeholders in generated templates |
| `app/copilot/providers/provider_manager.py` | `"mock"` provider alias |
| `app/copilot/extractors/architecture.py` | Placeholder module names comment |
| `app/team_analytics/metrics_aggregator.py` | Mock vulnerability count comment |
| `app/metrics/statistics_builder.py`, `app/rag/hybrid_ranker.py`, `app/copilot/extractors/parsing_utils.py` | `return {}` empty fallbacks |
| `app/agents/base_agent.py` | ABC `pass` (abstract, expected) |

**Automated stub count:** `NotImplementedError|pass$|return {}` across `app/**/*.py` ≈ **107** matches (includes abstract methods / benign empties — not all are broken endpoints).

#### `pip install -r requirements.txt`

- Environment: existing `backend/.venv`, Python **3.12.10**
- Result: **all requirements already satisfied** — no installation errors
- Notice only: pip upgrade available (25.0.1 → 26.2.1)

#### Cold start (`uvicorn app.main:app --host 127.0.0.1 --port 8000`)

| Check | Result |
| ----- | ------ |
| `python -c "import app.main"` | **PASS** (exit 0) |
| Application startup | **PASS** — `Application startup complete` |
| Uvicorn bind | **PASS** — `http://127.0.0.1:8000` |
| `GET /health` | **PASS** — `200` `{"status":"healthy","version":"1.0.0-rc.1"}` |
| `GET /` | **PASS** — `200` running status |
| Python exceptions in startup logs | **None** |
| Notes | PowerShell surfaces uvicorn INFO on stderr as `NativeCommandError`; not an app failure |

#### Debugging checklist (Phase 0)

- [x] Can you import `app.main` with zero errors? **Yes**
- [x] Is every file in `app/api/` reachable via the router? **Yes** — all 64 API modules included in `main.py` (plus `incremental_indexing` without prefix)
- [x] Does every model in `app/models/` have a corresponding migration? **N/A** — no Alembic migration tree; ORM tables live in `storage/models.py` and are created by `init_db()`. Copilot `app/copilot/models/` are Pydantic, not DB.
- [x] Does every service in `app/services/` have its dependencies injected — not globally instantiated? **No (gap recorded)** — services use module-level singletons (`upload_service`, `extraction_service`, etc.)
- [x] Is there a circular import? **Not on cold start** — `from app.main import app` succeeded

---

## PHASE 1 — FastAPI Startup

### Objective

The application starts with zero errors. `uvicorn app.main:app` runs successfully. `http://localhost:8000/docs` loads.

### Why This Phase Exists

Nothing else is testable until the application starts. Every subsequent phase depends on a working server.

### Files to Inspect

- `app/main.py`
- `app/core/config.py`
- `app/api/router.py` (or equivalent top-level router)
- Every file that is imported at startup

### APIs Involved

- `GET /` — health or root endpoint
- `GET /health` — health check (if present)
- `GET /docs` — Swagger UI

### Swagger Endpoints to Verify

- Swagger loads without JS errors
- All registered routers appear as tag groups

### Expected Request

```
GET /health HTTP/1.1
Host: localhost:8000
```

### Expected Response

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Success Criteria

- `uvicorn app.main:app --reload` starts with zero Python exceptions
- `GET /docs` returns HTTP 200
- `GET /health` returns HTTP 200 with a valid JSON body
- No `DeprecationWarning` from Pydantic V1 syntax in a V2 environment

### Manual Verification Steps

1. Create a fresh `.env` from `.env.example` with valid values
2. Run: `uvicorn app.main:app --reload --port 8000`
3. Open browser: `http://localhost:8000/docs`
4. Verify Swagger loads completely
5. Run: `curl -s http://localhost:8000/health | python -m json.tool`
6. Count the number of router groups visible in Swagger — record this number

### Automated Tests

```bash
# Start server in background and test health
uvicorn app.main:app --port 8000 &
sleep 3
curl -f http://localhost:8000/health && echo "PASS" || echo "FAIL"
kill %1
```

### Common Failure Points

- Pydantic V1 syntax (`validator`, `__fields__`) used in a V2 environment
- `app.include_router()` called with a module that has a top-level import error
- Database connection attempted at import time rather than at request time
- Missing `PYTHONPATH` causing relative import failures
- Lifespan event handler crashing silently

### Debugging Checklist

- [ ] Does `python -m app.main` produce a clean import?
- [ ] Is the lifespan handler (`@asynccontextmanager`) free of network calls that might fail on startup?
- [ ] Are all routers imported lazily or do they trigger DB connections at import time?
- [ ] Does `app.openapi()` return a valid OpenAPI dict? Run: `python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2)[:500])"`

### Exit Criteria

- [ ] Server starts in under 5 seconds
- [ ] `GET /health` returns HTTP 200
- [ ] Swagger UI fully loads with all route groups visible
- [ ] Zero Python exceptions or warnings in server logs

### Git Commit Suggestion

```
fix: fastapi startup clean — all routers load, health endpoint verified
```

### Completion Checklist

- [ ] Server starts cleanly
- [ ] `/health` passes
- [ ] Swagger loads
- [ ] Router count recorded

---

## PHASE 2 — Configuration

### Objective

Every configuration value is read correctly from environment variables. No hardcoded values exist in business logic. Settings are validated at startup.

### Why This Phase Exists

Misconfiguration is the most common silent failure mode. An endpoint that appears to work but reads from a hardcoded path will fail the moment it runs against a different machine.

### Files to Inspect

- `app/core/config.py`
- `app/core/settings.py` (if separate)
- `.env.example`
- Every file containing `os.environ.get` or `os.getenv`

### APIs Involved

- `GET /health` — should reflect configuration state
- Any config-introspection endpoint if present

### Swagger Endpoints to Verify

- None specific — this is a correctness phase

### Expected Request

N/A

### Expected Response

Settings object loads without validation errors.

### Success Criteria

- All settings use Pydantic `BaseSettings` with explicit types and validators
- No `os.getenv()` calls outside `config.py`
- Missing required environment variables produce a clear error at startup, not at request time
- Sensitive values (API keys, DB passwords) are never logged

### Manual Verification Steps

1. Remove one required environment variable from `.env`
2. Start the server — confirm it fails with a descriptive error message, not a traceback
3. Restore the variable
4. Run: `grep -rn "os.getenv\|os.environ" app/ --include="*.py"` — every result outside `config.py` is a bug
5. Print the settings object at startup (excluding secrets) and verify every value is correct

### Automated Tests

```bash
# Test that missing required var fails cleanly
unset DATABASE_URL
python -c "from app.core.config import settings" 2>&1 | grep -i "error\|missing\|required"
```

### Common Failure Points

- `Optional[str] = None` on a field that is actually required — hides misconfiguration
- Default values that work locally but fail in production (e.g., `localhost` database host)
- API keys defaulting to empty string instead of raising an error
- Config loaded multiple times, producing multiple DB connections

### Debugging Checklist

- [ ] Does every required setting raise a `ValidationError` if missing?
- [ ] Is the settings object a singleton (loaded once)?
- [ ] Are database URLs, storage paths, and API keys all externally configurable?
- [ ] Are there any hardcoded `localhost`, `127.0.0.1`, or absolute paths in service files?

### Exit Criteria

- [ ] All settings have explicit types in `BaseSettings`
- [ ] Missing required settings produce readable errors at startup
- [ ] Zero `os.getenv` calls outside `config.py`
- [ ] Settings object verified correct against `.env.example`

### Git Commit Suggestion

```
fix: config — all settings validated via pydantic, no raw os.getenv outside config.py
```

### Completion Checklist

- [ ] All settings typed
- [ ] Startup validation confirmed
- [ ] No stray `os.getenv` calls
- [ ] Secrets excluded from logs

---

## PHASE 3 — Environment Variables

### Objective

A complete, accurate `.env` file exists. Every variable the backend needs is documented and set. The backend runs identically whether started locally or in a container.

### Why This Phase Exists

Undocumented environment variables are a constant source of production failures. This phase forces completeness.

### Files to Inspect

- `.env.example`
- `.env` (local, never committed)
- `docker-compose.yml` (if present) — environment section
- `app/core/config.py` — source of truth for required variables

### APIs Involved

None — this is an infrastructure phase.

### Swagger Endpoints to Verify

None.

### Expected Request

N/A

### Expected Response

N/A

### Success Criteria

- `.env.example` contains every variable that `config.py` references
- Every variable has a comment explaining its purpose and acceptable values
- A developer with only `.env.example` can configure the backend correctly
- No variable is missing from `.env.example`

### Manual Verification Steps

1. Open `config.py` — list every field
2. Open `.env.example` — list every variable
3. Diff the two lists — any field in `config.py` not in `.env.example` is a gap
4. For every variable, verify the example value is realistic (not `YOUR_KEY_HERE` without explanation)
5. Test with a complete `.env` — server starts cleanly

### Automated Tests

```bash
# Extract all settings fields from config
python -c "
from app.core.config import Settings
import inspect
for name, field in Settings.model_fields.items():
    print(name, field.is_required())
"
```

### Common Failure Points

- New environment variables added to `config.py` but not added to `.env.example`
- Variables with confusing names that are not self-documenting
- Variables whose valid format is not documented (e.g., a URL vs a hostname)

### Debugging Checklist

- [ ] Does `.env.example` match `config.py` field-for-field?
- [ ] Are Groq/OpenAI/Anthropic API key variables present?
- [ ] Is the vector store configuration present?
- [ ] Is the storage path or S3 bucket configuration present?

### Exit Criteria

- [ ] `.env.example` is complete and accurate
- [ ] Every variable is commented
- [ ] Backend starts cleanly with `.env` populated from `.env.example`

### Git Commit Suggestion

```
docs: env — complete .env.example with all required variables and comments
```

### Completion Checklist

- [ ] `.env.example` is complete
- [ ] All variables are documented
- [ ] Clean startup confirmed

---

## PHASE 4 — Database

### Objective

The database connection is stable. All migrations are applied. All ORM models reflect the actual schema. CRUD operations work correctly.

### Why This Phase Exists

Every repository storage, indexing record, and analysis result depends on the database. A broken database layer silently corrupts everything above it.

### Files to Inspect

- `app/db/session.py` or `app/core/database.py`
- `app/models/` — all SQLAlchemy or Tortoise models
- `alembic/versions/` or `migrations/` — all migration files
- `alembic.ini` or `env.py`

### APIs Involved

Any endpoint that reads or writes repository metadata.

### Swagger Endpoints to Verify

- `GET /repositories` — depends on DB read
- `POST /repositories` — depends on DB write

### Expected Request

```
GET /repositories HTTP/1.1
Host: localhost:8000
```

### Expected Response

```json
{
  "repositories": [],
  "total": 0
}
```

(Empty list is correct before any uploads — not an error.)

### Success Criteria

- `alembic upgrade head` completes without errors
- Every model has a corresponding table in the database
- Session is created per-request, not globally
- Connection pool is configured (not unlimited)
- Database errors return HTTP 503 or 500 with a descriptive message, not a raw Python traceback

### Manual Verification Steps

1. Run: `alembic upgrade head`
2. Connect to database directly and run: `\dt` (PostgreSQL) or equivalent — list all tables
3. Compare table list against model list — every model must have a table
4. Run: `curl http://localhost:8000/repositories` — expect empty list, HTTP 200
5. Run: `curl -X POST http://localhost:8000/repositories -d '{}'` — expect validation error, not DB error
6. Intentionally break the DB connection string — verify the error message is human-readable

### Automated Tests

```bash
# Verify migrations are current
alembic current
alembic heads

# Run model tests
pytest tests/test_models.py -v
```

### Common Failure Points

- Migrations out of sync with models (model changed but migration not generated)
- Global session created at import time — causes connection leaks
- Missing `index=True` on foreign keys — causes full table scans on every repository lookup
- SQLAlchemy async session used with sync code or vice versa
- `autocommit=True` on a session that expects explicit transaction control

### Debugging Checklist

- [ ] Does `alembic upgrade head` complete with zero errors?
- [ ] Are all tables present in the database?
- [ ] Is the session dependency-injected via `Depends(get_db)` in every route?
- [ ] Are transactions explicitly committed or do you rely on autocommit?
- [ ] Is connection pooling configured with a max size?

### Exit Criteria

- [ ] `alembic upgrade head` passes
- [ ] All tables exist
- [ ] `GET /repositories` returns HTTP 200 with empty list
- [ ] DB connection errors produce readable error responses

### Git Commit Suggestion

```
fix: database — migrations applied, session per-request, connection pooling configured
```

### Completion Checklist

- [ ] Migrations current
- [ ] All tables verified
- [ ] CRUD test passed
- [ ] Error handling tested

---

## PHASE 5 — Storage

### Objective

File storage is operational. Uploaded ZIPs are stored and retrievable. Storage paths are configurable.

### Why This Phase Exists

Repository upload is the entry point to the entire platform. Without working storage, nothing else can be tested with real data.

### Files to Inspect

- `app/services/storage.py` or `app/core/storage.py`
- `app/core/config.py` — storage configuration
- Any S3 client or local filesystem abstraction

### APIs Involved

- `POST /repositories/upload` — writes to storage
- Any file retrieval endpoint

### Swagger Endpoints to Verify

- Upload endpoint accepts multipart form data
- Returns a storage path or file ID

### Expected Request

```
POST /repositories/upload HTTP/1.1
Content-Type: multipart/form-data

file: <zip_binary>
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "storage_path": "/uploads/uuid/repo.zip",
  "size_bytes": 104857600,
  "status": "uploaded"
}
```

### Success Criteria

- A ZIP file uploaded via the API is verifiably written to the storage location
- The stored file is byte-identical to the uploaded file (verify with MD5 or SHA256)
- Storage path is returned in the response and is a real path, not a placeholder
- Files from different repositories never overwrite each other (repository-scoped paths)
- A storage write failure returns HTTP 500 with a descriptive message

### Manual Verification Steps

1. Configure storage path in `.env`
2. Upload a real ZIP via Swagger: `POST /repositories/upload`
3. Navigate to the storage path and confirm the file exists
4. Run: `md5sum <original.zip>` and `md5sum <stored_file>` — hashes must match
5. Upload a second ZIP — confirm it is stored in a separate path
6. Fill storage to capacity (or mock a write failure) — confirm error response is correct

### Automated Tests

```bash
pytest tests/test_storage.py -v
```

### Common Failure Points

- Storage path not created before write (directory does not exist)
- No storage quota or size limit check before writing
- Concurrent uploads to the same path causing file corruption
- Presigned URLs expiring before the client reads the file

### Debugging Checklist

- [ ] Is the storage directory created on startup if it does not exist?
- [ ] Is the upload streamed or fully buffered? (Buffering a 50 MB file in memory will cause OOM on a small server)
- [ ] Are temporary files cleaned up after extraction?
- [ ] Is the storage service injected via dependency or globally instantiated?

### Exit Criteria

- [ ] Upload stores byte-identical file
- [ ] Storage path is repository-scoped
- [ ] Storage failures return correct error response
- [ ] No temporary file leaks

### Git Commit Suggestion

```
fix: storage — upload writes correctly, scoped paths, write failures handled
```

### Completion Checklist

- [ ] Upload stores file correctly
- [ ] MD5 verification passed
- [ ] Second upload uses separate path
- [ ] Error case tested

---

## PHASE 6 — Repository Upload

### Objective

`POST /repositories/upload` works end-to-end. A repository record is created in the database. The uploaded file is stored. The response contains all required fields.

### Why This Phase Exists

This is the first real user action in the system. Every downstream phase depends on a repository existing in the database.

### Files to Inspect

- `app/api/routes/repositories.py`
- `app/services/repository_service.py`
- `app/models/repository.py`
- `app/schemas/repository.py`

### APIs Involved

- `POST /repositories/upload`
- `GET /repositories/{repository_id}`

### Swagger Endpoints to Verify

- Upload endpoint visible in Swagger under the repositories tag
- Accepts `multipart/form-data` with a `file` field
- Returns repository metadata including status

### Expected Request

```
POST /repositories/upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="file"; filename="my-project.zip"
Content-Type: application/zip

<binary data>
------FormBoundary--
```

### Expected Response

```json
{
  "repository_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "my-project",
  "status": "uploaded",
  "size_bytes": 204800,
  "created_at": "2024-01-01T00:00:00Z",
  "storage_path": "uploads/3fa85f64/my-project.zip"
}
```

### Success Criteria

- Response status is HTTP 201
- `repository_id` is a valid UUID
- `status` is `"uploaded"` (not `"pending"` or `null`)
- `GET /repositories/{repository_id}` returns the same record
- Database row exists with correct values
- File exists at `storage_path`
- Uploading a non-ZIP returns HTTP 400 with a clear error message
- Uploading a file over the size limit returns HTTP 413

### Manual Verification Steps

1. Open Swagger at `/docs`
2. Expand `POST /repositories/upload`
3. Click "Try it out"
4. Upload a real ZIP file
5. Verify HTTP 201 response
6. Copy the `repository_id`
7. Run: `GET /repositories/{repository_id}` — verify same data
8. Query the database: `SELECT * FROM repositories WHERE id = '<uuid>';`
9. Check storage directory for the file
10. Upload a `.txt` file instead of `.zip` — verify HTTP 400

### Automated Tests

```bash
pytest tests/test_upload.py -v

# Manual curl test
curl -X POST http://localhost:8000/repositories/upload \
  -F "file=@test_repo.zip" \
  -H "Accept: application/json"
```

### Common Failure Points

- File type validation missing — accepts any file type
- `status` field set to `None` or left unset after upload
- Repository name extracted from filename incorrectly (e.g., retains `.zip` extension)
- Database write succeeds but storage write fails with no rollback
- Response schema does not match actual model fields

### Debugging Checklist

- [ ] Is file type validated before storage write?
- [ ] Is the repository name cleaned (no `.zip`, no path separators)?
- [ ] Is the database write inside a transaction with the storage write?
- [ ] Does the response schema include all required fields?
- [ ] Is the `created_at` timestamp set correctly?

### Exit Criteria

- [ ] HTTP 201 on valid upload
- [ ] HTTP 400 on non-ZIP file
- [ ] Database row verified
- [ ] Storage file verified
- [ ] `GET /repositories/{id}` returns correct data

### Git Commit Suggestion

```
feat: upload endpoint verified — real file storage, db write, schema correct
```

### Completion Checklist

- [ ] Upload returns HTTP 201
- [ ] Non-ZIP returns HTTP 400
- [ ] DB row verified
- [ ] File on disk verified

---

## PHASE 7 — ZIP Extraction

### Objective

Uploaded ZIP files are extracted correctly. File trees are produced accurately. Malicious or malformed ZIPs are rejected safely.

### Why This Phase Exists

The scanner and parser both depend on an extracted directory tree. If extraction is broken or unsafe, all analysis is wrong.

### Files to Inspect

- `app/services/extractor.py` or `app/core/extractor.py`
- Any service that calls `zipfile.ZipFile` or `shutil.unpack_archive`
- Extraction path configuration

### APIs Involved

- `POST /repositories/{id}/extract` (if separate endpoint exists)
- Or the upload endpoint if extraction is triggered automatically

### Swagger Endpoints to Verify

- Extraction status visible in repository status endpoint

### Expected Request

```
POST /repositories/{id}/extract HTTP/1.1
Host: localhost:8000
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "status": "extracted",
  "file_count": 142,
  "extraction_path": "workspace/uuid/extracted/",
  "extracted_at": "2024-01-01T00:00:05Z"
}
```

### Success Criteria

- All files from the ZIP are present in the extraction directory
- Nested directories are preserved
- File count in response matches actual file count on disk
- Zip Slip attack is prevented (paths with `../` are rejected)
- Password-protected ZIPs return HTTP 400 with a clear message
- Corrupt ZIPs return HTTP 400 with a clear message
- Extraction directory is scoped to the repository ID

### Manual Verification Steps

1. Upload a ZIP containing at least 3 nested directory levels
2. Trigger extraction
3. Navigate to the extraction directory and verify full structure
4. Run: `find <extraction_path> | wc -l` — compare to `file_count` in response
5. Craft a ZIP with a `../../../etc/passwd` path entry and upload it — verify rejection
6. Upload a password-protected ZIP — verify HTTP 400

### Automated Tests

```bash
pytest tests/test_extractor.py -v

# Zip Slip test
python -c "
import zipfile, io
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w') as z:
    z.writestr('../../../etc/evil.txt', 'exploit')
buf.seek(0)
with open('evil.zip', 'wb') as f:
    f.write(buf.read())
"
curl -X POST http://localhost:8000/repositories/upload -F "file=@evil.zip"
# Must return HTTP 400, not HTTP 201
```

### Common Failure Points

- Zip Slip not checked — path traversal allows writing files outside the extraction directory
- `zipfile.extractall()` called without path validation
- Symlinks inside ZIP followed — can escape extraction directory
- Extraction creates a nested extra directory (e.g., `extracted/repo-main/` instead of `extracted/`)
- No cleanup of previous extraction before re-extracting

### Debugging Checklist

- [ ] Is every path in the ZIP validated against the extraction root before extraction?
- [ ] Are symlinks inside the ZIP followed or skipped?
- [ ] Is the extraction path unique per repository (not shared)?
- [ ] Are old extraction directories cleaned up before re-extraction?
- [ ] Is file count computed from actual disk contents, not ZIP manifest?

### Exit Criteria

- [ ] Nested directory structure preserved
- [ ] File count accurate
- [ ] Zip Slip rejected
- [ ] Corrupt ZIP returns HTTP 400
- [ ] Extraction path is repository-scoped

### Git Commit Suggestion

```
fix: zip extraction — path traversal prevented, structure verified, error cases handled
```

### Completion Checklist

- [ ] Nested structure verified
- [ ] File count matches
- [ ] Zip Slip test passed
- [ ] Corrupt ZIP test passed

---

## PHASE 8 — Repository Persistence

### Objective

Repository records are correctly created, retrieved, listed, updated, and deleted. All status transitions are correct.

### Why This Phase Exists

The repository record is the anchor for all downstream data. Incorrect status values or missing fields will silently corrupt analysis results.

### Files to Inspect

- `app/models/repository.py`
- `app/schemas/repository.py`
- `app/services/repository_service.py`
- `app/api/routes/repositories.py`

### APIs Involved

- `GET /repositories` — list all
- `GET /repositories/{id}` — get one
- `DELETE /repositories/{id}` — delete
- `GET /repositories/{id}/status` — status check

### Swagger Endpoints to Verify

All four endpoints listed above.

### Expected Request

```
GET /repositories HTTP/1.1
```

### Expected Response

```json
{
  "repositories": [
    {
      "repository_id": "uuid",
      "name": "my-project",
      "status": "uploaded",
      "size_bytes": 204800,
      "file_count": 142,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### Success Criteria

- `GET /repositories` returns a paginated list
- `GET /repositories/{id}` returns 404 for non-existent ID
- `DELETE /repositories/{id}` removes the DB record, storage file, and extraction directory
- Status field is one of a defined enum — never `null`
- `updated_at` changes after any status update

### Manual Verification Steps

1. Upload two different repositories
2. `GET /repositories` — confirm both appear with correct fields
3. `GET /repositories/{id1}` — confirm correct data
4. `GET /repositories/nonexistent-uuid` — confirm HTTP 404
5. `DELETE /repositories/{id1}` — confirm HTTP 204
6. `GET /repositories` — confirm only one repository remains
7. Navigate to storage — confirm deleted repository's files are gone

### Automated Tests

```bash
pytest tests/test_repository_crud.py -v
```

### Common Failure Points

- `DELETE` removes the DB record but leaves files on disk
- `status` field returned as integer instead of string enum
- Pagination returns all records instead of page-sized chunks
- `GET /repositories/{id}` returns HTTP 500 for non-existent UUID instead of HTTP 404
- `updated_at` not refreshed when status changes

### Debugging Checklist

- [ ] Is the status field an enum with defined values?
- [ ] Does `DELETE` cascade to storage and extraction directory?
- [ ] Is pagination working (try page 2 with per_page=1)?
- [ ] Is UUID validation happening before the DB query?

### Exit Criteria

- [ ] List endpoint returns correct paginated data
- [ ] Get-one returns 404 for missing ID
- [ ] Delete removes DB record and files
- [ ] Status field is always a valid enum value

### Git Commit Suggestion

```
fix: repository persistence — crud verified, delete cascades to files, 404 on missing id
```

### Completion Checklist

- [ ] List endpoint verified
- [ ] Get-one verified
- [ ] Delete cascade verified
- [ ] 404 verified

---

## PHASE 9 — Repository Scanner

### Objective

The scanner produces a complete, accurate file tree from the extracted repository. Language detection is correct. Binary files are excluded.

### Why This Phase Exists

The file tree is the input to the parser. Inaccurate scanning means inaccurate parsing.

### Files to Inspect

- `app/services/scanner.py`
- `app/models/scan_result.py` (if present)
- `app/api/routes/scan.py` or equivalent

### APIs Involved

- `POST /repositories/{id}/scan`
- `GET /repositories/{id}/scan`

### Swagger Endpoints to Verify

Both endpoints.

### Expected Request

```
POST /repositories/{id}/scan HTTP/1.1
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "status": "scanned",
  "file_count": 142,
  "directory_count": 18,
  "languages": {
    "Python": 45,
    "JavaScript": 30,
    "Markdown": 20,
    "JSON": 10,
    "Other": 37
  },
  "total_size_bytes": 524288,
  "scanned_at": "2024-01-01T00:00:10Z"
}
```

### Success Criteria

- File count matches `find <extraction_path> -type f | wc -l`
- Language distribution is derived from file extensions, not hardcoded
- Binary files (images, compiled binaries, `.pyc`) are excluded from analysis
- Hidden directories (`.git`, `__pycache__`, `node_modules`) are excluded
- Scan result is stored in the database and retrievable via `GET /repositories/{id}/scan`

### Manual Verification Steps

1. Upload a real Python or JavaScript project ZIP
2. `POST /repositories/{id}/scan`
3. Compare `file_count` against: `find <extraction_path> -type f | grep -v ".git\|__pycache__\|node_modules" | wc -l`
4. Verify Python files are detected as Python
5. Verify `.pyc` files are excluded
6. Re-run the scan — verify idempotent result

### Automated Tests

```bash
pytest tests/test_scanner.py -v
```

### Common Failure Points

- `.git` directory included in file count (skews all metrics)
- Binary files included in language stats
- Language detected by content-sniffing is wrong for edge cases (prefer extension-based detection for speed)
- Scan result not stored — `GET` endpoint returns 404 after scan

### Debugging Checklist

- [ ] Is `.git` excluded from all file counts?
- [ ] Is `__pycache__` excluded?
- [ ] Is `node_modules` excluded?
- [ ] Are `.pyc`, `.class`, `.o` files excluded?
- [ ] Is the scan result persisted?

### Exit Criteria

- [ ] File count matches filesystem
- [ ] Languages accurately detected
- [ ] Excluded directories confirmed absent
- [ ] Scan result retrievable after scanning

### Git Commit Suggestion

```
fix: scanner — accurate file tree, language detection, exclusions, result persisted
```

### Completion Checklist

- [ ] File count verified
- [ ] Languages verified
- [ ] Exclusions verified
- [ ] Scan result persisted

---

## PHASE 10 — Parser

### Objective

The AST parser produces real symbol data from real source files. Functions, classes, imports, and exports are correctly extracted.

### Why This Phase Exists

The knowledge graph, dependency graph, and copilot all depend on accurate symbol extraction. Wrong symbols produce wrong intelligence.

### Files to Inspect

- `app/services/parser.py`
- Any Tree-sitter grammar files or configuration
- `app/models/symbol.py` or equivalent
- `app/api/routes/parser.py` or equivalent

### APIs Involved

- `POST /repositories/{id}/parse`
- `GET /repositories/{id}/symbols`

### Swagger Endpoints to Verify

Both endpoints.

### Expected Request

```
POST /repositories/{id}/parse HTTP/1.1
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "status": "parsed",
  "symbol_count": 312,
  "file_count_parsed": 75,
  "parse_errors": [],
  "parsed_at": "2024-01-01T00:00:20Z"
}
```

### Success Criteria

- Symbols are extracted from real source files
- Function definitions include name, line number, file path, and signature
- Class definitions include name, parent classes, and methods
- Import statements are extracted as edges in the dependency model
- Files that fail to parse are listed in `parse_errors` — not silently ignored
- Parse result is stored and retrievable

### Manual Verification Steps

1. Upload a Python project with known functions and classes
2. `POST /repositories/{id}/parse`
3. `GET /repositories/{id}/symbols`
4. Manually inspect a source file and verify its functions appear in the symbols list
5. Verify class inheritance is captured
6. Introduce a syntax error in a file — verify it appears in `parse_errors` rather than crashing the entire parse

### Automated Tests

```bash
pytest tests/test_parser.py -v
```

### Common Failure Points

- Tree-sitter grammar not installed for the target language
- Parser crashes on one bad file and stops — all subsequent files are silently skipped
- Line numbers off by one (0-indexed vs 1-indexed)
- Import paths stored as absolute instead of relative to repository root
- Parse results not committed to database

### Debugging Checklist

- [ ] Is parsing wrapped in per-file try/except so one bad file doesn't stop all parsing?
- [ ] Are line numbers 1-indexed (as editors display them)?
- [ ] Are import paths relative to the repository root?
- [ ] Is the Tree-sitter binary for the required language actually installed?
- [ ] Are parse results stored in the database?

### Exit Criteria

- [ ] Symbols extracted from real source files
- [ ] Line numbers correct
- [ ] Parse errors captured, not silently ignored
- [ ] Parse results stored and retrievable

### Git Commit Suggestion

```
fix: parser — real symbols extracted, per-file error isolation, results persisted
```

### Completion Checklist

- [ ] Symbols verified against source
- [ ] Line numbers verified
- [ ] Parse errors isolated
- [ ] Results stored

---

## PHASE 11 — Repository Indexing

### Objective

The full indexing pipeline runs successfully: scan → parse → chunk → embed → store. The repository is marked `READY` when complete.

### Why This Phase Exists

Indexing is the pipeline that converts raw source code into queryable intelligence. Until indexing completes, no analysis endpoint can return real data.

### Files to Inspect

- `app/services/indexer.py`
- `app/services/chunker.py`
- `app/api/routes/indexing.py`
- `app/models/index_record.py`

### APIs Involved

- `POST /repositories/{id}/index`
- `GET /repositories/{id}/index/status`
- `GET /repositories/{id}/index/progress`

### Swagger Endpoints to Verify

All three endpoints.

### Expected Request

```
POST /repositories/{id}/index HTTP/1.1
```

### Expected Response (status poll)

```json
{
  "repository_id": "uuid",
  "status": "indexing",
  "progress_percent": 45,
  "current_stage": "embedding",
  "stages_complete": ["scan", "parse", "chunk"],
  "stages_remaining": ["embed", "store"],
  "started_at": "2024-01-01T00:00:00Z",
  "estimated_completion": "2024-01-01T00:02:00Z"
}
```

### Success Criteria

- Indexing progresses through all stages without hanging
- `progress_percent` increments during indexing (not stuck at 0 or 100)
- Repository status changes to `READY` when indexing completes
- `GET /repositories/{id}/index/status` is accurate while indexing is running
- Indexing a repository twice does not create duplicate records
- Failed indexing sets status to `FAILED` with an error message — never leaves it at `indexing`

### Manual Verification Steps

1. Upload and extract a repository
2. `POST /repositories/{id}/index`
3. Poll `GET /repositories/{id}/index/status` every 2 seconds for 60 seconds
4. Verify `progress_percent` increases
5. Verify final status is `READY`
6. Query database: `SELECT status FROM repositories WHERE id = '<uuid>';` — must be `READY`
7. Index the same repository again — verify no duplicate records

### Automated Tests

```bash
pytest tests/test_indexer.py -v
```

### Common Failure Points

- Indexing hangs at a specific stage with no error
- `progress_percent` stays at 0 throughout
- Status remains `indexing` after completion due to missing status update
- Duplicate chunk records created on re-index
- Embedding API rate-limit hit without retry logic

### Debugging Checklist

- [ ] Is each stage explicitly updating the progress in the database?
- [ ] Is there a timeout on each stage?
- [ ] Is re-indexing idempotent (deletes existing records before creating new ones)?
- [ ] Is the embedding API call wrapped in retry logic with exponential backoff?
- [ ] Does the final stage update repository status to `READY`?

### Exit Criteria

- [ ] All stages complete
- [ ] Status transitions to `READY`
- [ ] Progress increments
- [ ] Re-index is idempotent
- [ ] Failure sets status to `FAILED`

### Git Commit Suggestion

```
fix: indexing pipeline — all stages complete, status transitions correct, re-index idempotent
```

### Completion Checklist

- [ ] Full pipeline completed on real repo
- [ ] Status is `READY`
- [ ] Progress tracked
- [ ] Re-index tested

---

## PHASE 12 — Embeddings

### Objective

Chunks are embedded using the configured embedding model. Embeddings are stored in the vector database. Similarity queries return relevant results.

### Why This Phase Exists

RAG retrieval depends entirely on the quality and correctness of stored embeddings. Corrupted or missing embeddings silently degrade all AI responses.

### Files to Inspect

- `app/services/embedder.py`
- `app/services/vector_store.py`
- Vector store client configuration (Qdrant, ChromaDB, FAISS, etc.)
- `app/core/config.py` — embedding model and vector store settings

### APIs Involved

- Embedding is triggered by the indexing pipeline — no standalone endpoint
- `POST /repositories/{id}/search` — tests embedding quality via retrieval

### Swagger Endpoints to Verify

- `POST /repositories/{id}/search`

### Expected Request

```json
POST /repositories/{id}/search
{
  "query": "authentication logic",
  "top_k": 5,
  "filters": {}
}
```

### Expected Response

```json
{
  "results": [
    {
      "chunk_id": "uuid",
      "content": "def authenticate_user(username, password):\n    ...",
      "file_path": "app/auth/service.py",
      "start_line": 42,
      "end_line": 58,
      "score": 0.91,
      "language": "Python"
    }
  ],
  "query": "authentication logic",
  "total_results": 5
}
```

### Success Criteria

- `POST /repositories/{id}/search` returns relevant results for semantic queries
- Results include real file paths and content from the actual repository
- Scores are between 0 and 1
- No results reference files that do not exist in the repository
- Searching a repository that has not been indexed returns HTTP 400 or 404 with a clear message

### Manual Verification Steps

1. Complete indexing on a real repository
2. `POST /repositories/{id}/search` with query: `"main entry point"`
3. Verify returned file paths exist in the repository
4. Open the returned files and verify the returned content is actually there
5. Try a query for something that definitely doesn't exist: verify empty results, not an error
6. Count chunks in the vector store: must be greater than zero

### Automated Tests

```bash
pytest tests/test_embeddings.py -v
pytest tests/test_vector_store.py -v
```

### Common Failure Points

- Embedding API key not set — all embeddings silently fail or are zero vectors
- Zero vectors stored — all search results return the same documents regardless of query
- Chunks stored without file path metadata — results are not attributable to source files
- Vector store collection created but embeddings never written due to batching error
- Score threshold filters all results — returns empty even for clearly relevant queries

### Debugging Checklist

- [ ] Is the embedding API key correctly configured?
- [ ] Are stored vectors non-zero? (Query a known chunk and check its vector)
- [ ] Does each stored chunk include file path, start line, end line, and content?
- [ ] Is the vector store collection created before writing?
- [ ] Is there a minimum score threshold that might be filtering all results?

### Exit Criteria

- [ ] Vector store contains non-zero embeddings
- [ ] Search returns relevant results for semantic queries
- [ ] Results include real file content and paths
- [ ] Empty query result returns empty list, not an error

### Git Commit Suggestion

```
fix: embeddings — vectors non-zero, metadata complete, search returns relevant results
```

### Completion Checklist

- [ ] Vectors verified non-zero
- [ ] Search returns real results
- [ ] File paths verified in results
- [ ] Empty query case tested

---

## PHASE 13 — Repository Memory

### Objective

Repository Memory APIs return accurate per-repository summaries, context, and intelligence derived from real repository data.

### Why This Phase Exists

Repository Memory is the structured intelligence layer between raw code and the AI copilot. Without it, the copilot has no grounded context.

### Files to Inspect

- `app/services/repository_memory.py`
- `app/api/routes/memory.py`
- `app/models/memory.py`

### APIs Involved

- `GET /repositories/{id}/memory`
- `GET /repositories/{id}/memory/summary`
- `GET /repositories/{id}/memory/context`

### Swagger Endpoints to Verify

All three endpoints.

### Expected Request

```
GET /repositories/{id}/memory/summary HTTP/1.1
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "summary": "This is a Flask web application implementing a REST API for task management. It uses SQLAlchemy for database access, JWT for authentication, and is structured following the repository pattern.",
  "key_modules": ["auth", "tasks", "users", "database"],
  "primary_language": "Python",
  "framework": "Flask",
  "generated_at": "2024-01-01T00:05:00Z"
}
```

### Success Criteria

- `summary` is a real AI-generated description of the actual repository — not a template
- `key_modules` are real directories or packages from the repository
- `framework` matches the detected framework from the scanner
- All memory endpoints return HTTP 400 for repositories that are not yet indexed
- Memory is cached — repeated calls do not trigger repeated LLM calls

### Manual Verification Steps

1. Index a real repository
2. `GET /repositories/{id}/memory/summary`
3. Read the summary — verify it accurately describes the repository you uploaded
4. Compare `key_modules` against actual top-level directories
5. Compare `framework` against scanner result
6. Call `GET /repositories/{id}/memory/summary` again — verify identical response (cached)
7. Call on unindexed repository — verify HTTP 400

### Automated Tests

```bash
pytest tests/test_repository_memory.py -v
```

### Common Failure Points

- Summary is a generic template not derived from repository content
- `key_modules` is the full file list instead of meaningful modules
- LLM called on every request — no caching
- Memory built on scanner data only — not on actual parsed symbols

### Debugging Checklist

- [ ] Is the summary generated from actual file content?
- [ ] Is the LLM response cached per repository?
- [ ] Are `key_modules` derived from parsed structure, not guessed?
- [ ] Does the endpoint handle unindexed repositories gracefully?

### Exit Criteria

- [ ] Summary accurately describes uploaded repository
- [ ] `key_modules` match actual structure
- [ ] Caching confirmed (second call is faster)
- [ ] Unindexed repository returns correct error

### Git Commit Suggestion

```
fix: repository memory — real summaries, caching implemented, unindexed guard added
```

### Completion Checklist

- [ ] Summary verified accurate
- [ ] Modules verified correct
- [ ] Cache verified
- [ ] Unindexed guard tested

---

## PHASE 14 — RAG Retrieval

### Objective

The RAG pipeline retrieves relevant, grounded context and delivers it to the LLM. Responses are based on actual repository content.

### Why This Phase Exists

The copilot's answer quality depends entirely on retrieval quality. A broken RAG pipeline produces confident but wrong answers — worse than no answer.

### Files to Inspect

- `app/services/rag.py` or `app/services/retriever.py`
- `app/services/context_builder.py`
- `app/services/llm_client.py` or `app/core/llm.py`
- Prompt templates

### APIs Involved

- `POST /repositories/{id}/rag/query`
- `GET /repositories/{id}/rag/context`

### Swagger Endpoints to Verify

Both endpoints.

### Expected Request

```json
POST /repositories/{id}/rag/query
{
  "query": "How does authentication work in this project?",
  "max_tokens": 1000,
  "top_k": 5
}
```

### Expected Response

```json
{
  "answer": "Authentication in this project is implemented using JWT tokens. The `authenticate_user` function in `app/auth/service.py` validates credentials against the database. On success, it calls `create_access_token` which signs a JWT with the secret key configured in settings...",
  "sources": [
    {
      "file_path": "app/auth/service.py",
      "start_line": 42,
      "content": "def authenticate_user(...)",
      "relevance_score": 0.93
    }
  ],
  "query": "How does authentication work?",
  "tokens_used": 750
}
```

### Success Criteria

- Answer references specific functions, classes, or files from the actual repository
- `sources` are real, verifiable chunks from real files
- Answer is never a generic response unrelated to the repository
- Queries about something that doesn't exist in the repository return an honest "I don't find evidence of this in the codebase" — not a hallucinated answer
- Token count is reported accurately

### Manual Verification Steps

1. Index a real repository
2. `POST /repositories/{id}/rag/query` with `"query": "what is the main entry point?"`
3. Read the answer — verify it references a real file from the repository
4. Open that file — verify the referenced function or logic actually exists there
5. Ask about something that definitely doesn't exist in the repo
6. Verify the answer honestly says it cannot find this
7. Check `sources` — every source must be a real file from the repository

### Automated Tests

```bash
pytest tests/test_rag.py -v
```

### Common Failure Points

- LLM answer is not grounded in retrieved chunks (hallucination)
- Sources returned are from a different repository (tenant isolation bug)
- Context window overflow — LLM receives truncated context with no warning
- Empty sources list but non-empty answer (LLM is making up an answer)
- LLM API key not configured — returns 500 on every query

### Debugging Checklist

- [ ] Is the context injected into the prompt before the question?
- [ ] Are retrieved chunks from the correct repository (filtered by repository_id)?
- [ ] Is context length checked before sending to LLM?
- [ ] Is the LLM API key correctly configured and tested?
- [ ] Are sources returned only for chunks that were actually included in the prompt?

### Exit Criteria

- [ ] Answer references real files from repository
- [ ] Sources are verifiable in the repository
- [ ] Non-existent topics produce honest "not found" response
- [ ] Token count accurate

### Git Commit Suggestion

```
fix: rag — grounded answers, real sources, context length checked, tenant isolation verified
```

### Completion Checklist

- [ ] Answer verified against source files
- [ ] Sources verified in repository
- [ ] "Not found" case tested
- [ ] Tenant isolation tested

---

## PHASE 15 — Dashboard Backend APIs

### Objective

All dashboard endpoints return real analysis data from indexed repositories. No placeholder values remain.

### Why This Phase Exists

The dashboard is the primary UI entry point. Returning dummy data here means the frontend shows fake metrics that could mislead any user of the platform.

### Files to Inspect

- `app/api/routes/dashboard.py`
- `app/services/analytics.py`
- `app/services/quality_analyzer.py`
- `app/services/security_analyzer.py`
- `app/services/metrics.py`

### APIs Involved

- `GET /repositories/{id}/overview`
- `GET /repositories/{id}/metrics`
- `GET /repositories/{id}/quality`
- `GET /repositories/{id}/security`
- `GET /repositories/{id}/architecture`
- `GET /repositories/{id}/dependencies`
- `GET /repositories/{id}/risks`
- `GET /repositories/{id}/health`

### Swagger Endpoints to Verify

All eight endpoints.

### Expected Request

```
GET /repositories/{id}/overview HTTP/1.1
```

### Expected Response

```json
{
  "repository_id": "uuid",
  "name": "my-project",
  "file_count": 142,
  "language_count": 4,
  "primary_language": "Python",
  "detected_frameworks": ["Flask", "SQLAlchemy"],
  "health_score": 72,
  "risk_level": "medium",
  "total_size_bytes": 524288,
  "indexed_at": "2024-01-01T00:05:00Z"
}
```

### Success Criteria

- Every field is derived from real repository analysis, not hardcoded
- `health_score` is computed from quality, security, and maintainability metrics
- `detected_frameworks` match what the scanner found
- `file_count` matches the scanner result
- All endpoints return HTTP 400 for repositories not yet indexed

### Manual Verification Steps

1. Index a real Python Flask project
2. `GET /repositories/{id}/overview` — verify `primary_language` is `Python`
3. Verify `detected_frameworks` includes Flask
4. `GET /repositories/{id}/metrics` — verify file count matches scanner
5. `GET /repositories/{id}/quality` — verify quality issues reference real files
6. `GET /repositories/{id}/security` — verify findings are real, not templated
7. Call each endpoint on an unindexed repository — confirm HTTP 400

### Automated Tests

```bash
pytest tests/test_dashboard.py -v
```

### Common Failure Points

- `health_score` hardcoded to 72 regardless of actual code quality
- `detected_frameworks` returns empty array for all repositories
- `risk_level` always returns `"medium"` regardless of actual risks
- Quality issues returned without file paths (not attributable to real code)
- Metrics computed from placeholder counts instead of scanner results

### Debugging Checklist

- [ ] Is `health_score` computed from real analyzer results?
- [ ] Does the quality endpoint return file paths and line numbers for every issue?
- [ ] Are `detected_frameworks` populated from scanner data?
- [ ] Is `risk_level` derived from actual risk analysis?
- [ ] Do all endpoints guard against unindexed repositories?

### Exit Criteria

- [ ] Every field verified as real for at least two different repositories
- [ ] Framework detection matches scanner
- [ ] Quality issues include real file paths
- [ ] All endpoints return correct error for unindexed repos

### Git Commit Suggestion

```
fix: dashboard apis — all fields real data, no placeholders, unindexed guard on all endpoints
```

### Completion Checklist

- [ ] Overview verified
- [ ] Metrics verified
- [ ] Quality verified
- [ ] Security verified
- [ ] Architecture verified
- [ ] Dependencies verified

---

## PHASE 16 — Copilot Backend APIs

### Objective

The Copilot API accepts a question, retrieves relevant context via RAG, calls the LLM, and returns a grounded, accurate response. Conversation history is preserved.

### Why This Phase Exists

The copilot is the highest-value feature. A copilot that returns generic or hallucinated answers is worse than no copilot — it destroys trust.

### Files to Inspect

- `app/api/routes/copilot.py`
- `app/services/copilot_service.py`
- `app/services/conversation_manager.py`
- `app/services/llm_client.py`
- Prompt templates for the copilot

### APIs Involved

- `POST /repositories/{id}/copilot/chat`
- `GET /repositories/{id}/copilot/conversations`
- `GET /repositories/{id}/copilot/conversations/{conversation_id}`
- `DELETE /repositories/{id}/copilot/conversations/{conversation_id}`

### Swagger Endpoints to Verify

All four endpoints.

### Expected Request

```json
POST /repositories/{id}/copilot/chat
{
  "message": "Explain how database connections are managed in this project",
  "conversation_id": null
}
```

### Expected Response

```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "answer": "Database connections in this project are managed through SQLAlchemy's session factory defined in `app/db/session.py`. The `get_db` function creates a session per request using...",
  "sources": [
    {
      "file_path": "app/db/session.py",
      "content": "def get_db():\n    db = SessionLocal()\n    try:\n        yield db\n    finally:\n        db.close()",
      "relevance_score": 0.95
    }
  ],
  "tokens_used": 820,
  "created_at": "2024-01-01T00:10:00Z"
}
```

### Success Criteria

- Response references real files and real code from the repository
- `sources` are verifiable in the repository
- Follow-up messages in the same `conversation_id` are contextually aware of prior turns
- `GET /conversations/{id}` returns the full message history
- `DELETE /conversations/{id}` removes the conversation
- Asking about something not in the codebase produces an honest response
- LLM API error returns HTTP 503 with a retry suggestion

### Manual Verification Steps

1. `POST /repositories/{id}/copilot/chat` — send a question about the repository
2. Verify the answer references a real file
3. Open that file and verify the referenced logic exists
4. Send a follow-up question in the same `conversation_id`
5. Verify the follow-up response shows awareness of the prior question
6. `GET /repositories/{id}/copilot/conversations` — verify conversation appears
7. `GET /repositories/{id}/copilot/conversations/{id}` — verify full message history
8. `DELETE /repositories/{id}/copilot/conversations/{id}` — verify HTTP 204
9. Ask about something not in the codebase — verify honest "not found" response

### Automated Tests

```bash
pytest tests/test_copilot.py -v
```

### Common Failure Points

- Conversation history not passed to LLM — every message is treated as independent
- LLM API key not set in production environment
- Sources in response reference files from a different repository
- Follow-up questions lose context from previous turns
- Streaming endpoint (`text/event-stream`) closes connection before full response

### Debugging Checklist

- [ ] Is `conversation_id` passed to the retriever to filter context by conversation?
- [ ] Is conversation history included in the prompt to the LLM?
- [ ] Are sources scoped to `repository_id`?
- [ ] Is the LLM API response validated before returning to client?
- [ ] Is the streaming endpoint tested with an actual streaming client?

### Exit Criteria

- [ ] First message returns grounded answer with real sources
- [ ] Follow-up message is context-aware
- [ ] Conversation history retrievable
- [ ] Delete conversation works
- [ ] LLM error returns HTTP 503

### Git Commit Suggestion

```
fix: copilot api — grounded responses, conversation history, sources scoped to repo
```

### Completion Checklist

- [ ] First message verified
- [ ] Follow-up verified context-aware
- [ ] History retrieval verified
- [ ] Delete verified
- [ ] LLM error case tested

---

## PHASE 17 — Authentication and Authorization

### Objective

If authentication is implemented, it works correctly. Every protected endpoint returns HTTP 401 without a valid token. Every public endpoint remains accessible without a token.

### Why This Phase Exists

Authentication bugs are security vulnerabilities. A route that should require auth but doesn't is a data exposure risk.

### Files to Inspect

- `app/core/auth.py` or `app/services/auth_service.py`
- `app/api/dependencies.py` — auth dependency
- `app/api/routes/auth.py` — login/token endpoints
- Every router file — verify which routes use the auth dependency

### APIs Involved

- `POST /auth/login` or `POST /auth/token`
- `POST /auth/logout`
- `GET /auth/me`
- Every protected endpoint

### Swagger Endpoints to Verify

- Auth endpoints visible and functional
- Swagger "Authorize" button works with a valid token
- Protected endpoints return 401 without authorization

### Expected Request

```json
POST /auth/login
{
  "username": "developer@example.com",
  "password": "secure_password"
}
```

### Expected Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Success Criteria

- Invalid credentials return HTTP 401 — never HTTP 500
- Valid token grants access to protected resources
- Expired token returns HTTP 401 — not HTTP 500
- Token with tampered signature returns HTTP 401
- If auth is not implemented, all endpoints are public and this phase is marked N/A

### Manual Verification Steps

1. If auth is not implemented: document this explicitly and move on
2. `POST /auth/login` with valid credentials — verify token returned
3. `GET /auth/me` with valid token — verify correct user data returned
4. `GET /repositories` without token — verify HTTP 401
5. `GET /repositories` with expired token — verify HTTP 401
6. `GET /repositories` with tampered token — verify HTTP 401
7. `POST /auth/login` with wrong password — verify HTTP 401, not HTTP 500

### Automated Tests

```bash
pytest tests/test_auth.py -v
```

### Common Failure Points

- JWT secret key set to a weak default in development and copied to production
- `Optional` token dependency that silently accepts no token (auth is bypassed)
- Token expiry not checked on protected routes
- Password comparison using `==` instead of constant-time comparison

### Debugging Checklist

- [ ] Is the JWT secret key a strong random value in production?
- [ ] Is token expiry validated on every request?
- [ ] Is password comparison constant-time?
- [ ] Are ALL intended-protected routes actually protected?
- [ ] Does Swagger's Authorize button actually restrict access?

### Exit Criteria

- [ ] Auth is either fully working or explicitly documented as N/A
- [ ] Protected routes return 401 without valid token
- [ ] Login with wrong credentials returns 401
- [ ] Expired token returns 401

### Git Commit Suggestion

```
fix: auth — token validation correct, all protected routes guarded, 401 on invalid credentials
```

### Completion Checklist

- [ ] Auth status documented (implemented or N/A)
- [ ] Protected routes verified
- [ ] Invalid credentials tested
- [ ] Expired token tested

---

## PHASE 18 — Background Jobs and Events

### Objective

Background tasks (indexing, scanning, embedding) run asynchronously and reliably. Task status is queryable. Failed tasks are surfaced, not silently dropped.

### Why This Phase Exists

Long-running operations cannot block the HTTP request. A broken background job system means indexing never completes and the user never knows why.

### Files to Inspect

- `app/workers/` or `app/tasks/`
- Celery configuration if used (`celery_app.py`)
- `app/services/job_queue.py` or equivalent
- Any `asyncio.create_task` or `BackgroundTasks` usage in route handlers

### APIs Involved

- `GET /jobs/{job_id}` — job status
- `GET /repositories/{id}/index/status` — indexing job status

### Swagger Endpoints to Verify

Job status endpoint.

### Expected Request

```
GET /jobs/{job_id} HTTP/1.1
```

### Expected Response

```json
{
  "job_id": "uuid",
  "job_type": "indexing",
  "status": "running",
  "progress_percent": 65,
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "error": null
}
```

### Success Criteria

- Indexing runs in the background without blocking the POST response
- Job status is queryable while the job is running
- Failed jobs set status to `FAILED` with an error message
- Jobs do not silently hang — there is a timeout
- Completed jobs have a `completed_at` timestamp

### Manual Verification Steps

1. `POST /repositories/{id}/index` — note the immediate response (should be HTTP 202 Accepted)
2. Immediately poll `GET /repositories/{id}/index/status` — verify `status` is `running`
3. Poll every 5 seconds for up to 5 minutes — verify progress increments
4. Verify final status is `READY` with `completed_at` set
5. Kill the background worker mid-job — verify status eventually transitions to `FAILED`

### Automated Tests

```bash
pytest tests/test_background_jobs.py -v
```

### Common Failure Points

- `BackgroundTasks` in FastAPI runs in the same process — a crash kills the request handler too
- Celery workers not started — tasks queue but never run
- No timeout on tasks — a hanging embedding call blocks forever
- Job status not updated on success — remains `running` forever
- Task exception swallowed — status never transitions to `FAILED`

### Debugging Checklist

- [ ] Is there a separate worker process for background jobs?
- [ ] Is the job status updated at every stage transition?
- [ ] Is there a timeout on the longest-running stage?
- [ ] Are task exceptions caught and written to the job record?
- [ ] Is the Celery worker (if used) running alongside the API server?

### Exit Criteria

- [ ] Indexing returns HTTP 202 immediately
- [ ] Job status queryable while running
- [ ] Status transitions to `READY` on success
- [ ] Status transitions to `FAILED` on error
- [ ] Completed jobs have `completed_at` set

### Git Commit Suggestion

```
fix: background jobs — async indexing, status updates correct, failure captured
```

### Completion Checklist

- [ ] HTTP 202 on indexing start
- [ ] Status queryable
- [ ] Success transition verified
- [ ] Failure transition verified

---

## PHASE 19 — Error Handling

### Objective

Every possible error scenario returns a consistent, structured error response. No endpoint returns a raw Python traceback. No endpoint silently returns HTTP 200 with error content.

### Why This Phase Exists

Inconsistent error responses make the frontend impossible to build reliably. Raw tracebacks leak internal implementation details and are a security risk.

### Files to Inspect

- `app/core/exceptions.py`
- `app/main.py` — global exception handlers
- Every route handler — verify try/except blocks

### APIs Involved

Every endpoint.

### Swagger Endpoints to Verify

All error responses are documented in Swagger schemas.

### Expected Error Response Format

```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "Repository with ID 'abc123' does not exist.",
    "detail": null,
    "request_id": "req_xyz789"
  }
}
```

### Success Criteria

- Every HTTP 4xx and 5xx response uses the above structure
- No endpoint returns a raw Python traceback
- HTTP 404 for resource not found — never HTTP 500
- HTTP 400 for validation errors with field-level detail
- HTTP 422 for malformed request bodies (Pydantic validation)
- HTTP 500 only for truly unexpected errors — never for known failure modes
- All error codes are documented

### Manual Verification Steps

1. `GET /repositories/nonexistent-uuid` — verify 404 with correct error structure
2. `POST /repositories/upload` with a non-ZIP — verify 400 with correct error structure
3. `POST /repositories/upload` with no file — verify 422 with field-level error
4. Force a DB error (stop the DB) — verify 503, not 500 with traceback
5. Check every 4xx response body — verify it matches the error schema
6. Verify no response contains `Traceback`, `File "`, or `line` (raw Python traceback markers)

### Automated Tests

```bash
pytest tests/test_error_handling.py -v

# Check for raw tracebacks in responses
grep -r "Traceback\|File \"" tests/responses/ 2>/dev/null && echo "RAW TRACEBACK FOUND" || echo "CLEAN"
```

### Common Failure Points

- FastAPI's default 422 Unprocessable Entity response not overridden — exposes internal field names
- `except Exception as e: return {"error": str(e)}` — leaks implementation details
- DB connection failure returns 500 with full SQLAlchemy traceback
- Missing global exception handler — unhandled exceptions produce FastAPI's default error format which may differ from your error schema

### Debugging Checklist

- [ ] Is there a global exception handler registered in `app.main`?
- [ ] Is Pydantic's 422 response overridden to use the project error schema?
- [ ] Do all custom exceptions inherit from a base `AppException` class?
- [ ] Is `request_id` attached to every error response for log correlation?

### Exit Criteria

- [ ] All 4xx responses match error schema
- [ ] All 5xx responses match error schema
- [ ] No raw tracebacks in any response
- [ ] Every error code is documented

### Git Commit Suggestion

```
fix: error handling — consistent schema, no tracebacks, all known errors use 4xx
```

### Completion Checklist

- [ ] 404 format verified
- [ ] 400 format verified
- [ ] 422 format verified
- [ ] 503 format verified
- [ ] No raw tracebacks confirmed

---

## PHASE 20 — Performance Validation

### Objective

All endpoints respond within acceptable time limits under single-user load. No endpoint takes more than 5 seconds for non-AI operations. No memory leaks under repeated calls.

### Why This Phase Exists

A correct but slow API is not production-ready. Performance problems discovered after deployment are expensive to fix.

### Files to Inspect

- All service files — look for N+1 query patterns
- Database query patterns — check for missing indexes
- Any endpoint that calls the LLM synchronously in a request handler

### APIs Involved

All endpoints.

### Swagger Endpoints to Verify

Response time headers on all endpoints.

### Benchmarks

```
GET /health                 < 50ms
GET /repositories           < 200ms
GET /repositories/{id}      < 200ms
POST /repositories/upload   < 10s (dependent on file size)
POST /repositories/{id}/scan < 30s (dependent on file count)
POST /repositories/{id}/parse < 60s (dependent on file count)
GET /repositories/{id}/overview < 500ms (cached)
POST /repositories/{id}/search  < 2s
POST /copilot/chat               < 30s (LLM dependent)
```

### Success Criteria

- Every non-AI endpoint responds within the benchmark
- No N+1 queries on list endpoints
- Database queries use indexes for lookups by `repository_id`
- Overview and summary endpoints use caching (second call is at least 10x faster than first)
- Memory usage does not grow on repeated API calls (no leak)

### Manual Verification Steps

1. Time each endpoint: `time curl -s http://localhost:8000/repositories/{id}/overview`
2. Enable SQLAlchemy query logging and inspect queries on list endpoints
3. Call `GET /repositories/{id}/overview` twice — second call must be significantly faster
4. Make 100 consecutive calls to `GET /repositories` and monitor memory: `ps aux | grep uvicorn`

### Automated Tests

```bash
# Install locust or use ab
ab -n 100 -c 10 http://localhost:8000/health

pytest tests/test_performance.py -v
```

### Common Failure Points

- `SELECT *` on the repositories table for every request in a list
- Dependency graph computed fresh on every request instead of being cached
- LLM called synchronously in the request handler — blocks the event loop
- File system scanned on every metrics request instead of reading from database

### Debugging Checklist

- [ ] Are list endpoints paginated and indexed?
- [ ] Are computed results (architecture, metrics, quality) cached in the database?
- [ ] Are LLM calls non-blocking?
- [ ] Is there a connection pool limit preventing thread exhaustion?

### Exit Criteria

- [ ] All benchmarks met
- [ ] No N+1 queries on list endpoints
- [ ] Caching confirmed on overview/summary endpoints
- [ ] No memory growth under repeated calls

### Git Commit Suggestion

```
perf: all endpoints within benchmark, caching confirmed, no n+1 queries
```

### Completion Checklist

- [ ] All benchmarks met
- [ ] N+1 queries eliminated
- [ ] Caching verified
- [ ] Memory stability confirmed

---

## PHASE 21 — Final Swagger Validation

### Objective

Every single endpoint in the API passes all checks. The backend is declared complete.

### Why This Phase Exists

This is the final gate. No endpoint is forgotten. No endpoint is half-working.

### Complete Endpoint Validation Table

For each endpoint, open Swagger, execute the request, and mark PASS or FAIL.

---

#### Repository Endpoints

| Endpoint                        | Purpose     | Request       | Expected Response    | Real Data? | Error Tested?          | Status |
| ------------------------------- | ----------- | ------------- | -------------------- | ---------- | ---------------------- | ------ |
| `POST /repositories/upload`     | Upload ZIP  | multipart ZIP | 201 + repo metadata  | ✓          | ZIP/size invalid → 400 |        |
| `GET /repositories`             | List repos  | none          | 200 + paginated list | ✓          | empty list → 200       |        |
| `GET /repositories/{id}`        | Get repo    | repo ID       | 200 + repo metadata  | ✓          | unknown ID → 404       |        |
| `DELETE /repositories/{id}`     | Delete repo | repo ID       | 204                  | ✓          | unknown ID → 404       |        |
| `GET /repositories/{id}/status` | Get status  | repo ID       | 200 + status enum    | ✓          | unknown ID → 404       |        |

#### Scan Endpoints

| Endpoint                       | Purpose         | Request | Expected Response | Real Data? | Error Tested?      | Status |
| ------------------------------ | --------------- | ------- | ----------------- | ---------- | ------------------ | ------ |
| `POST /repositories/{id}/scan` | Trigger scan    | repo ID | 202 + job ID      | ✓          | not uploaded → 400 |        |
| `GET /repositories/{id}/scan`  | Get scan result | repo ID | 200 + scan data   | ✓          | not scanned → 404  |        |

#### Parse Endpoints

| Endpoint                         | Purpose       | Request | Expected Response | Real Data? | Error Tested?     | Status |
| -------------------------------- | ------------- | ------- | ----------------- | ---------- | ----------------- | ------ |
| `POST /repositories/{id}/parse`  | Trigger parse | repo ID | 202 + job ID      | ✓          | not scanned → 400 |        |
| `GET /repositories/{id}/symbols` | Get symbols   | repo ID | 200 + symbol list | ✓          | not parsed → 404  |        |

#### Indexing Endpoints

| Endpoint                                | Purpose       | Request | Expected Response | Real Data? | Error Tested?      | Status |
| --------------------------------------- | ------------- | ------- | ----------------- | ---------- | ------------------ | ------ |
| `POST /repositories/{id}/index`         | Trigger index | repo ID | 202 + job ID      | ✓          | not parsed → 400   |        |
| `GET /repositories/{id}/index/status`   | Index status  | repo ID | 200 + progress    | ✓          | not indexing → 404 |        |
| `GET /repositories/{id}/index/progress` | Progress %    | repo ID | 200 + percent     | ✓          | not indexing → 404 |        |

#### Dashboard Endpoints

| Endpoint                              | Purpose          | Request | Expected Response       | Real Data? | Error Tested?     | Status |
| ------------------------------------- | ---------------- | ------- | ----------------------- | ---------- | ----------------- | ------ |
| `GET /repositories/{id}/overview`     | Overview         | repo ID | 200 + summary           | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/metrics`      | Metrics          | repo ID | 200 + metrics           | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/quality`      | Quality          | repo ID | 200 + quality issues    | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/security`     | Security         | repo ID | 200 + security findings | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/architecture` | Architecture     | repo ID | 200 + arch diagram      | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/dependencies` | Dependency graph | repo ID | 200 + graph data        | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/risks`        | Risk analysis    | repo ID | 200 + risk list         | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/health`       | Health score     | repo ID | 200 + score             | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/timeline`     | Timeline         | repo ID | 200 + events            | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/impact`       | Impact analysis  | repo ID | 200 + impact            | ✓          | not indexed → 400 |        |

#### Search and Retrieval Endpoints

| Endpoint                            | Purpose         | Request    | Expected Response     | Real Data? | Error Tested?     | Status |
| ----------------------------------- | --------------- | ---------- | --------------------- | ---------- | ----------------- | ------ |
| `POST /repositories/{id}/search`    | Semantic search | query JSON | 200 + results         | ✓          | not indexed → 400 |        |
| `POST /repositories/{id}/rag/query` | RAG query       | query JSON | 200 + grounded answer | ✓          | not indexed → 400 |        |

#### Memory Endpoints

| Endpoint                                | Purpose     | Request | Expected Response   | Real Data? | Error Tested?     | Status |
| --------------------------------------- | ----------- | ------- | ------------------- | ---------- | ----------------- | ------ |
| `GET /repositories/{id}/memory`         | Full memory | repo ID | 200 + memory object | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/memory/summary` | Summary     | repo ID | 200 + summary text  | ✓          | not indexed → 400 |        |
| `GET /repositories/{id}/memory/context` | Context     | repo ID | 200 + context       | ✓          | not indexed → 400 |        |

#### Copilot Endpoints

| Endpoint                                                | Purpose      | Request      | Expected Response      | Real Data? | Error Tested?     | Status |
| ------------------------------------------------------- | ------------ | ------------ | ---------------------- | ---------- | ----------------- | ------ |
| `POST /repositories/{id}/copilot/chat`                  | Send message | message JSON | 200 + answer + sources | ✓          | LLM error → 503   |        |
| `GET /repositories/{id}/copilot/conversations`          | List convos  | repo ID      | 200 + convo list       | ✓          | none → empty list |        |
| `GET /repositories/{id}/copilot/conversations/{cid}`    | Get convo    | convo ID     | 200 + message history  | ✓          | unknown ID → 404  |        |
| `DELETE /repositories/{id}/copilot/conversations/{cid}` | Delete convo | convo ID     | 204                    | ✓          | unknown ID → 404  |        |

#### System Endpoints

| Endpoint            | Purpose      | Request | Expected Response | Real Data? | Error Tested? | Status |
| ------------------- | ------------ | ------- | ----------------- | ---------- | ------------- | ------ |
| `GET /health`       | Health check | none    | 200 + status      | ✓          | N/A           |        |
| `GET /docs`         | Swagger UI   | none    | 200 HTML          | ✓          | N/A           |        |
| `GET /openapi.json` | OpenAPI spec | none    | 200 JSON          | ✓          | N/A           |        |

---

### Final Validation Procedure

Execute the following sequence using a real repository ZIP:

```
1. Upload repository → record repository_id
2. Scan repository   → verify file count
3. Parse repository  → verify symbol count
4. Index repository  → wait for READY status
5. Search           → verify relevant results
6. RAG query        → verify grounded answer
7. Copilot chat     → verify answer references real file
8. Dashboard overview → verify all fields real
9. Quality analysis → verify issues reference real files
10. Security analysis → verify findings reference real code
```

If every step produces real, accurate data: the backend is complete.

---

## DEVELOPMENT RULES

These rules apply from Phase 0 to Phase 21 without exception.

**Execution Rules:**

- Never work on two backend systems simultaneously. One phase at a time.
- Never begin the next phase until all Exit Criteria of the current phase are satisfied.
- Every completed phase must be committed to git with the suggested commit message.
- Never skip manual Swagger testing. Automated tests do not replace manual verification.
- Never use placeholder responses. If a value cannot be computed, return an error — not a fake value.
- Never ignore failing tests. A failing test is a failing endpoint.

**Debugging Rules:**

- Always identify the root cause before implementing a fix.
- Never fix a symptom. Fix the cause.
- Always reproduce the bug with a minimal test case before fixing it.
- Read the full error message and traceback before searching online.

**Quality Rules:**

- Never optimize before correctness. Make it right, then make it fast.
- Never add features before fixing existing bugs.
- Never move to the next phase with a known unresolved bug in the current phase.
- Every endpoint must be tested with real repository data before being marked complete.
- A response is not "real data" if it is computed from a hardcoded value anywhere in the call chain.

**Git Rules:**

- Keep commits small and focused. One fix per commit.
- Commit messages must describe what changed and why.
- Never commit with failing tests.
- Update this document after every phase completion.

**Documentation Rules:**

- Update the Completion Checklist of each phase when it is done.
- Mark the Final Swagger Validation table as PASS or FAIL for each endpoint.
- If a phase uncovers a problem in a prior phase, go back and fix the prior phase first.

---

## PHASE COMPLETION TRACKER

| Phase | Name                     | Status     | Commit | Date |
| ----- | ------------------------ | ---------- | ------ | ---- |
| 0     | Repository Sanity Check  | ✅ Complete | pending commit (`chore: phase 0 complete — repository audit, all gaps documented`) | 2026-08-05 |
| 1     | FastAPI Startup          | ⬜ Pending | —      | —    |
| 2     | Configuration            | ⬜ Pending | —      | —    |
| 3     | Environment Variables    | ⬜ Pending | —      | —    |
| 4     | Database                 | ⬜ Pending | —      | —    |
| 5     | Storage                  | ⬜ Pending | —      | —    |
| 6     | Repository Upload        | ⬜ Pending | —      | —    |
| 7     | ZIP Extraction           | ⬜ Pending | —      | —    |
| 8     | Repository Persistence   | ⬜ Pending | —      | —    |
| 9     | Repository Scanner       | ⬜ Pending | —      | —    |
| 10    | Parser                   | ⬜ Pending | —      | —    |
| 11    | Repository Indexing      | ⬜ Pending | —      | —    |
| 12    | Embeddings               | ⬜ Pending | —      | —    |
| 13    | Repository Memory        | ⬜ Pending | —      | —    |
| 14    | RAG Retrieval            | ⬜ Pending | —      | —    |
| 15    | Dashboard Backend APIs   | ⬜ Pending | —      | —    |
| 16    | Copilot Backend APIs     | ⬜ Pending | —      | —    |
| 17    | Authentication           | ⬜ Pending | —      | —    |
| 18    | Background Jobs          | ⬜ Pending | —      | —    |
| 19    | Error Handling           | ⬜ Pending | —      | —    |
| 20    | Performance Validation   | ⬜ Pending | —      | —    |
| 21    | Final Swagger Validation | ⬜ Pending | —      | —    |

**Backend rebuild is complete when all 22 rows show ✅ Complete.**
