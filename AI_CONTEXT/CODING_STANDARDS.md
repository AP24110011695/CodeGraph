# Coding Standards — Discovered from CodeGraph Repository

> **Only conventions actually used in this repo.**  
> **Related:** [AI_RULES.md](./AI_RULES.md) · [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## Folder structure (actual)

```text
CodeGraph/
├── AI_CONTEXT/           # AI permanent knowledge base (this folder)
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI app + router registration + lifespan
│   │   ├── api/          # Thin HTTP routers
│   │   ├── schemas/      # Pydantic models
│   │   ├── core/         # Settings
│   │   ├── <domain>/     # Business packages (engines, analyzers)
│   │   ├── services/     # Shared services (scanner, dependency_graph, upload, …)
│   │   ├── parsers/      # Parsing
│   │   ├── analyzers/    # Architecture builder models
│   │   ├── ai/           # LLM/prompt helpers
│   │   └── ...
│   ├── tests/            # pytest modules test_*.py
│   ├── uploads/          # Uploaded/demo repos
│   └── requirements.txt
├── frontend/             # Separate UI tree
└── README.md             # Human overview (partially outdated)
```

---

## Naming conventions

| Kind | Pattern | Example |
|------|---------|---------|
| Package | `snake_case` | `impact_analysis`, `repository_memory` |
| Engine facade | `*_engine.py` + class `FooEngine` | `timeline_engine.py` |
| Singleton | `foo_engine = FooEngine()` | module bottom |
| Analyzer | descriptive noun | `hotspot_detector.py` |
| API router file | matches domain | `api/timeline.py` |
| Schema file | matches domain | `schemas/timeline.py` |
| Tests | `test_<domain>.py` | `test_impact_analysis.py` |
| HTTP prefix | kebab or short noun | `/repository-memory`, `/impact` |
| Cache key namespace | snake constants on `CacheKeys` | `IMPACT_ANALYSIS` |

---

## Dependency Injection

Observed pattern:

```python
def __init__(self, collaborator: Optional[Collaborator] = None, cache: Optional[CacheInterface] = None):
    self.collaborator = collaborator or Collaborator()
    self._cache = cache or cache_manager
```

- Production: import module singleton.  
- Tests: pass fakes / custom providers (`HistoryProvider`, `graph_provider`).

---

## API conventions

- `APIRouter(prefix="...", tags=[...])`
- Register in `app/main.py` via `app.include_router(...)` — **required** or tests 404.
- Prefer path params `{repository_id}` / `{upload_id}` as used by the domain.
- `HTTPException` mapping in router `try/except`.
- Static subpaths before parameterized catch-alls (see Timeline routes).

---

## Schema conventions

- Pydantic v2 `BaseModel` + `Field(description=...)`.
- Request/response models colocated in `app/schemas/<feature>.py`.
- Nested result models for structured intelligence payloads.

---

## Testing conventions

- `pytest` + `fastapi.testclient.TestClient`.
- Fixture-style setup clearing cache namespaces when caching is under test.
- Assert status codes, key payload fields, and integration with planning/agents when relevant.
- Keep regression checks for neighboring modules.

---

## Logging

- `logger = logging.getLogger(__name__)`
- Info at facade boundaries; debug for optional skip paths.

---

## Telemetry

- `with telemetry_manager.track("domain.operation", component="domain"):`
- `telemetry_manager.increment("domain.operation")`
- HTTP middleware sets/returns `X-Correlation-ID`.

---

## Caching

- Always go through `cache_manager` / `CacheInterface`.
- Add helpers on `CacheKeys`.
- Store JSON-friendly dicts from `model_dump(mode="json")`.
- Invalidate by namespace prefix in tests (`cache_manager.invalidate("impact_analysis:")`).

---

## Planning

- Extend `QueryClassifier` for new intents **carefully** (order matters — timeline phrases before generic explain).
- Update `ExecutionPlanner`, `RetrievalStrategy`, `ReasoningStrategy` together.

---

## Agent architecture

- Subclass `BaseAgent` with `name`, `description`, `capabilities`, `execute`.
- Register in `agent_manager.py`.
- Map intent → agent names in `CollaborationEngine._map_intent_to_agents`.
- Agents call engines; no agent-to-agent calls.

---

## Service / module organization

- Shared I/O-ish utilities often live in `app/services/`.
- Domain intelligence lives in dedicated packages with `__init__.py` exporting facades.
- Prefer package-local helpers over new top-level utility dumping grounds.

---

## Error handling

- Routers: convert exceptions to HTTP errors.  
- Engines: optional enrichment failures swallowed with debug logs.
