# CHANGELOG_AI — AI-Friendly Module Changelog

> Append one section per completed CG module.  
> **Related:** [LESSONS_LEARNED.md](./LESSONS_LEARNED.md) · [ROADMAP.md](./ROADMAP.md)

---

## Final Polish — Portfolio & Open-Source Packaging

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **Milestone** | Public GitHub / portfolio readiness on RC-1 |

### Files added

- `PROJECT_ASSETS/**`  
- `docs/architecture/OVERVIEW.md`, `docs/api/OVERVIEW.md`, `docs/README.md`  
- `.github/workflows/ci.yml`, issue templates  
- `SECURITY.md`, `RELEASE_NOTES.md`  
- Populated `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`

### Files removed

- Empty duplicate `backend/{analyzers,graph,parsers,prompts}`  
- `backend/openapi.json` (empty), `backend/test_api.py`, `backend/test_jobs_api.py`

### Validation

- Re-run full pytest after polish (target: still green)

---

## RC-1 — Release Candidate 1 Stabilization

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **Milestone** | RC-1 (`1.0.0-rc.1`) |

### Files added

- `backend/app/core/paths.py`  
- `backend/tests/test_rc1_readiness.py`

### Files modified

- `backend/app/main.py` (register quality/smells/refactoring; version; health/root; reasoning router order)  
- `backend/app/core/config.py`  
- `backend/app/api/quality.py`, `smells.py`, `refactoring.py`, `architecture_reasoning.py`  
- `backend/tests/test_chat_api.py`  
- `backend/.env.example`  
- `README.md`, `backend/README.md`  
- AI_CONTEXT living docs

### Files removed

- `backend/debug_chunker.py`, `debug_chunker2.py`, `debug_chunker3.py`, `debug_chunker4.py`

### Architecture changes

- Closed API registration gap for quality/smells/refactoring.  
- Shared repository path resolver for dual-root consistency.  
- Safer default error exposure for architecture reasoning.

### Breaking changes

- None intended. Root/health JSON gained fields (`version`, `release`, `environment`) while retaining prior keys.

### Validation

- **1221 passed / 0 failed / 0 skipped**

---

## CG-070 — Unified Intelligence Orchestrator (CodeGraph Copilot)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **CG Module** | CG-070 |

### Files added

- `backend/app/copilot/conversation_manager.py`  
- `backend/app/copilot/conversation_memory.py`  
- `backend/app/copilot/context_builder.py`  
- `backend/app/copilot/prompt_builder.py`  
- `backend/app/copilot/tool_executor.py`  
- `backend/app/copilot/provider_manager.py`  
- `backend/app/copilot/post_processor.py`  
- `backend/app/copilot/execution_statistics.py`

### Files modified

- `backend/app/copilot/__init__.py`  
- `backend/app/copilot/copilot_engine.py`  
- `backend/app/copilot/response_builder.py`  
- `backend/app/api/copilot.py`  
- `backend/app/schemas/copilot.py`  
- `backend/tests/test_copilot.py`  
- AI_CONTEXT living docs

### Architecture changes

- Copilot upgraded from keyword capability routing to Planning-driven orchestration composing Memory, RAG, Reasoning, Timeline, Impact, Reports, and Agents.  
- Conversation memory separated from Repository Memory.  
- Pluggable tool registry + LLM provider manager.

### Breaking changes

- None for legacy `POST /copilot/{upload_id}`. New preferred APIs: `/copilot/chat`, `/copilot/execute`, `/copilot/history`.

### Design improvements

- Structured engineering responses with confidence, citations, recommendations, follow-ups, execution stats.

---

## CG-069 — Engineering Intelligence Report Generator

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **CG Module** | CG-069 |

### Files added

- `backend/app/engineering_reports/` (engine, collector, section composer, health scorer, exporters, store)  
- `backend/app/api/engineering_reports.py`  
- `backend/app/schemas/engineering_reports.py`  
- `backend/tests/test_engineering_reports.py`

### Files modified

- `backend/app/main.py`  
- `backend/app/cache/cache_keys.py`  
- `backend/app/copilot/capability_registry.py`  
- `backend/tests/test_cache.py`  
- AI_CONTEXT living docs

### Architecture changes

- New composed reporting layer over Memory, Reasoning, Timeline, Impact.  
- Pluggable export formats (JSON/Markdown live; HTML/PDF reserved).

### Breaking changes

- None.

### Design improvements

- Report types: executive, architecture, technical_debt, repository_health, security_overview, impact_analysis, custom.

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **CG Module** | CG-068 |

### Files added

- `backend/app/impact_analysis/` (engine, dependency/architecture/api/memory impact, propagation, risk, statistics, `__init__`)  
- `backend/app/api/impact_analysis.py`  
- `backend/app/schemas/impact_analysis.py`  
- `backend/app/agents/builtin/impact_agent.py`  
- `backend/tests/test_impact_analysis.py`

### Files modified

- `backend/app/main.py`  
- `backend/app/cache/cache_keys.py`  
- `backend/app/planning/*` (classifier, execution, retrieval, reasoning)  
- `backend/app/agents/agent_manager.py`, `collaboration_engine.py`, `builtin/dependency_agent.py`  
- `backend/app/copilot/capability_registry.py`  
- `backend/tests/test_agents.py`, `test_cache.py`  
- Living AI_CONTEXT status/roadmap/lessons/changelog/module index

### Architecture changes

- Predictive impact layer composing GraphQuery/RelationshipTraverser, Semantic SymbolResolver, Memory, Timeline.  
- Response surfaces: affected modules/services/APIs/symbols/repository memory + `impact_summary`.  
- Planning `impact_analysis` intent routes to Impact Analysis Engine; ImpactAgent registered.

### Breaking changes

- None intended for existing APIs (additive response fields).

### Design improvements

- Git/PR/CI-ready `related_files` / `change_type`.  
- Injectable `graph_provider` for real Knowledge Graphs.  
- Memory enrichment notes `[Impact]`.

---

## CG-067 — Repository Timeline Intelligence

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **CG Module** | CG-067 |

### Files added

- `backend/app/timeline/` (history provider, engine, analyzers, statistics)  
- `backend/app/api/timeline.py`  
- `backend/app/schemas/timeline.py`  
- `backend/app/agents/builtin/timeline_agent.py`  
- `backend/tests/test_timeline.py`

### Files modified

- `main.py`, cache keys, planning strategies/classifier, agents, RAG context/query/engine, copilot registry, related tests

### Architecture changes

- Temporal intelligence knowledge source with pluggable history providers.  
- `timeline_analysis` planning intent + TimelineAgent.

### Breaking changes

- None intended.

### Design improvements

- Local metadata provider reuses Memory + Snapshots; VCS stubs reserved.

---

## CG-001 … CG-066 — Foundation

| Field | Value |
|-------|-------|
| **Date** | Cumulative (pre-2026-07-31 operating assumption) |
| **CG Module** | CG-001 through CG-066 |

### Summary

Ingest, structure, quality/governance engines, integrations, platform (cache/telemetry/workflows/workers), semantic/memory/RAG/reasoning/planning/agents — present as packages under `backend/app/` with routers registered in `main.py` (except known quality/smells/refactoring API registration debt).

### Files

See [MODULE_INDEX.md](./MODULE_INDEX.md) for locations.

### Breaking changes

- N/A (baseline).

---

## AI_CONTEXT knowledge base bootstrap

| Field | Value |
|-------|-------|
| **Date** | 2026-07-31 |
| **CG Module** | Documentation / AI_CONTEXT (not a product CG engine ticket) |

### Files added

- Entire `AI_CONTEXT/` tree (rules, architecture, roadmap, vision, standards, status, debt, lessons, prompts, README_AI, changelog, module index)

### Architecture changes

- None to runtime code; establishes permanent AI operating documentation.

### Breaking changes

- None.
