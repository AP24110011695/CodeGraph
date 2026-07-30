# AI Rules — CodeGraph Permanent Engineering Rules

> **Authority:** This document is permanent. Change it rarely and only when project-wide engineering policy changes.  
> **Related:** [ARCHITECTURE.md](./ARCHITECTURE.md) · [CODING_STANDARDS.md](./CODING_STANDARDS.md) · [PROMPT_GUIDELINES.md](./PROMPT_GUIDELINES.md)

---

## Project philosophy

CodeGraph is an **Enterprise AI Software Architecture Platform**, not a code-search toy.

Every module must:

1. Increase architectural understanding of a repository.
2. Reuse existing intelligence instead of rebuilding it.
3. Remain composable, testable, and replaceable behind abstractions.
4. Move the product toward planning, multi-agent collaboration, memory, and reasoning over codebases.

See [PROJECT_VISION.md](./PROJECT_VISION.md).

---

## Architecture principles

### SOLID

- **S** — One module / class owns one responsibility (e.g. `HotspotDetector` detects hotspots; `TimelineEngine` orchestrates).
- **O** — Extend via new providers/analyzers; do not fork stable engines.
- **L** — Substitutable providers (e.g. `HistoryProvider`, `CacheInterface`) must honor the same contracts.
- **I** — Prefer narrow facades (`analyze`, `get_summary`, `plan`) over god-interfaces.
- **D** — Depend on abstractions and injectable collaborators; default to module singletons for production wiring.

### DRY

- Never copy business logic between packages.
- Prefer composition of existing engines over parallel implementations.

### Composition over inheritance

- Engines compose analyzers (`ImpactEngine` → `DependencyImpact` + `ChangePropagation` + …).
- Agents compose engines; agents do **not** call other agents directly (planner/dispatcher owns orchestration).

### Dependency Injection

- Constructors accept optional collaborators (`Optional[X] = None`) and default to shared singletons.
- Global facades (`timeline_engine`, `impact_engine`, `memory_engine`, `planning_engine`, `cache_manager`, `telemetry_manager`) are the production wiring style observed in this repo.
- Tests may inject fakes/providers without rewriting business logic.

### Separation of Concerns

| Layer | Responsibility |
|-------|----------------|
| `app/api/` | HTTP only — validate, call engine, map errors |
| `app/schemas/` | Pydantic request/response contracts |
| `app/<domain>/` | Business logic, analyzers, facades |
| `app/core/` | Settings / config |
| Infrastructure (`cache`, `telemetry`, `workflows`, `workers`, …) | Cross-cutting platform concerns |

### Thin API Layer / Thin Controller Pattern

- Routers must not implement analysis algorithms.
- Routers catch exceptions and raise `HTTPException`; engines own domain errors and logging.

---

## Reuse mandates (non-negotiable)

| Rule | Meaning |
|------|---------|
| **Reuse existing modules** | Before writing new code, search `backend/app/` for an engine that already solves the problem. |
| **Never duplicate business logic** | No second risk scorer, smell detector, or architecture builder “for convenience”. |
| **Never duplicate retrieval** | Use Semantic Engine / RAG / Memory / Graph query paths already present. |
| **Never duplicate indexing** | Use `indexing` + `incremental_indexing`; do not rescan/re-embed inside new features. |
| **Never duplicate graph traversal** | Use `GraphQuery`, `RelationshipTraverser`, or existing graph APIs — do not reimplement BFS/DFS. |
| **Never bypass Planning Engine** | Multi-agent and high-level query orchestration should go through planning intents when agents are involved. |
| **Never bypass Repository Memory** | Prefer enriching / reading memory over inventing a parallel “summary store”. |

---

## Validation requirements

After every CG module:

1. Run `python -m pytest tests/ -v` from `backend/`.
2. Start the API (`uvicorn app.main:app`) and hit new endpoints.
3. Verify related integrations still work (Planning, Agents, Memory, Cache, Telemetry as applicable).
4. Confirm no **new** regressions. Pre-existing failures must be documented in [TECH_DEBT.md](./TECH_DEBT.md), not ignored silently.

---

## Testing requirements

- Add focused tests under `backend/tests/test_<feature>.py`.
- Cover: core engine behavior, API happy paths, DI/provider seams, and regression of neighboring systems.
- Prefer `TestClient(app)` for API tests; inject fakes for unit seams.
- Do not delete or skip failing tests to “make green” without fixing root cause or recording debt.

---

## Coding conventions

See [CODING_STANDARDS.md](./CODING_STANDARDS.md) for repository-derived detail. Summary:

- Package per capability under `backend/app/<name>/`.
- Facade `*_engine.py` + module singleton.
- Schemas in `backend/app/schemas/<name>.py`.
- Router in `backend/app/api/<name>.py`, registered in `app/main.py`.

---

## Error handling conventions

- Domain/API boundary: `try/except` in routers → `HTTPException(status_code=…, detail=str(exc))`.
- Enrichment / optional integrations: catch and log/debug; **never** fail the primary operation because optional context failed (pattern used by Timeline/Impact/RAG enrichment).

---

## Logging conventions

- `logging.getLogger(__name__)` per module.
- Log at engine entry points (`logger.info("…Engine: …")`).
- Use `logger.debug` for skipped optional enrichment.

---

## Telemetry conventions

- Use `telemetry_manager.track(operation, component=…)` around significant work.
- Increment counters for operations (`timeline.generate`, `impact.analyze`, etc.).
- HTTP middleware already wraps requests with correlation IDs (`X-Correlation-ID`).

---

## Cache usage

- Use `cache_manager` / `CacheInterface`.
- Add namespaced keys via `CacheKeys` — never hard-code ad-hoc key strings in new modules.
- Cache serialized pydantic dumps (`model_dump(mode="json")`) with TTL when responses are expensive.

---

## Workflow usage

- Long-running repository processing steps belong in `workflows` definitions / registry when extending the pipeline.
- Do not invent a parallel orchestration framework.

---

## Agent usage

- New agent capabilities subclass `BaseAgent`, register in `agent_manager` / `agent_registry`.
- Map intents in `CollaborationEngine` and (when needed) `QueryClassifier` / Planning strategies.
- Agents call engines; they do not reimplement engine logic.

---

## Output format required after every implementation

Return exactly:

1. Files created  
2. Files modified  
3. Architecture summary (or folder tree when relevant)  
4. Test summary  
5. Validation summary  
6. Design decisions  
7. Self review  

Also update living docs per [PROMPT_GUIDELINES.md](./PROMPT_GUIDELINES.md):

- `CURRENT_STATUS.md`
- `ROADMAP.md`
- `LESSONS_LEARNED.md`
- `CHANGELOG_AI.md`
- `MODULE_INDEX.md`
- `TECH_DEBT.md` (if debt changed)
