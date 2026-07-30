# Module Index — CodeGraph Backend Master Index

> Master catalog of implemented subsystems. Update when modules are added.  
> **Related:** [ARCHITECTURE.md](./ARCHITECTURE.md) · [CHANGELOG_AI.md](./CHANGELOG_AI.md)

Legend: **API registered** = included in `app/main.py`.

---

## Platform & cross-cutting

| Name | Location | Responsibility | Dependencies | Used By | Public APIs | Related Tests | Future dependents |
|------|----------|----------------|--------------|---------|-------------|---------------|-------------------|
| FastAPI App | `app/main.py` | Router registration, lifespan, telemetry middleware | All routers | Clients | `/`, `/health` | Many API tests | All new routers |
| Settings | `app/core/config.py` | Env settings | pydantic-settings | App | — | — | Config expansion |
| Distributed Cache | `app/cache/` | CacheInterface, MemoryCache, CacheKeys | — | Semantic, Timeline, Impact, … | `/cache` | `test_cache.py` | Redis backend |
| Telemetry | `app/telemetry/` | Metrics, tracing, logs, health | Cache (metrics snapshot) | Middleware, engines | `/telemetry` | `test_telemetry.py` | Dashboards |
| Workflows | `app/workflows/` | DAG registry/executor; `repository_processing` | Steps/context | Pipeline orchestration | `/workflows` | `test_workflows.py` | New pipeline steps |
| Workers | `app/workers/` | Worker pool | Reliability | Lifespan, jobs | `/workers` | (workflows/reliability) | Scale-out |
| Jobs | `app/jobs/` | Async job queue/manager | Workers | Analysis jobs | `/jobs` | `test_jobs.py` | Heavy analyses |
| Events | `app/events/` | In-process bus | — | Publishers/subscribers | `/events` | `test_events.py` | Kafka migration |
| Repository State | `app/repository_state/` | Lifecycle state machine | — | Pipeline | `/repository-state` | `test_repository_state.py` | Workflows |
| Reliability | `app/reliability/` | Retry, circuit breaker, DLQ, timeouts | — | Lifespan, workers | `/reliability` | `test_reliability.py` | All async work |

---

## Ingest & structure

| Name | Location | Responsibility | Dependencies | Used By | Public APIs | Related Tests | Future dependents |
|------|----------|----------------|--------------|---------|-------------|---------------|-------------------|
| Upload | `app/services/upload_service.py`, `api/upload.py` | Accept repositories | Filesystem | Indexing | `/upload` | scanner/upload-related | Workflows |
| Scanner | `app/services/scanner_service.py` | File inventory | FS | Most analyzers | `/scan` | `test_scanner_*.py` | All structure |
| Framework Detector | `app/services/framework_detector.py` | Detect frameworks | Scanner | Architecture, reports | `/frameworks` | `test_framework_*.py` | Memory |
| Parser Engine | `app/parsers/` | AST/project parse | Scanner | Graphs, quality, UML | `/parse` | `test_parser_engine.py` | KG |
| Dependency Graph | `app/services/dependency_graph.py` | Import/dep graph | Scanner | KG, architecture, MS | `/dependency-graph` | `test_dependency_graph_*.py` | Impact via KG |
| Architecture Builder | `app/analyzers/` | Architecture models | Parser/graph | Drift, risk, reports | `/architecture` | `test_architecture_*.py` | Reasoning |
| Diagrams / Visualization | `app/visualization/` | Diagram models/generation | Architecture | API diagrams | `/diagrams` | `test_diagrams_api.py`, `test_diagram_generator.py` | Reports |
| UML | `app/uml/` | UML generation | Relationships | API uml | `/uml` | `test_uml_api.py` | Docs |
| Indexing | `app/indexing/` | Index orchestration | Upload/parse | Many engines via IndexManager | `/index` | indexing-related | Incremental |
| Incremental Indexing / Snapshots | `app/incremental_indexing/` | Change sets, snapshot evolve | Indexing | Timeline provider | `/incremental-indexing` (router) | `test_incremental_indexing.py`, `test_snapshot_evolution.py` | Timeline/Git |

---

## Knowledge & intelligence core

| Name | Location | Responsibility | Dependencies | Used By | Public APIs | Related Tests | Future dependents |
|------|----------|----------------|--------------|---------|-------------|---------------|-------------------|
| Knowledge Graph | `app/knowledge_graph/` | Unified graph + GraphQuery | Many analyzers | Memory, Semantic, Impact, RAG | `/knowledge-graph` | `test_knowledge_graph.py` | All reasoning |
| Semantic Engine | `app/semantic/` | Search, hybrid retrieve, traverse | Cache, graph provider | RAG, search | `/semantic` | `test_semantic.py` | Copilot |
| Search / RAG embeddings | `app/rag/` (embedding, retriever, vector pieces) + search API | Embeddings & retrieval | Index | Semantic/RAG | `/search`, `/rag` | `test_embedding_service.py`, `test_vector_store.py`, `test_retriever.py`, `test_rag_*.py` | Vector DB |
| Repository Memory | `app/repository_memory/` | Structured memory | KG | RAG, Reasoning, Timeline, Impact, Agents | `/repository-memory` | `test_repository_memory.py` | All NL features |
| Advanced RAG | `app/rag/rag_engine.py` et al. | LLM context composition | Memory, Semantic, Graph, Timeline | Planning/RAG API | `/rag` | `test_rag_engine.py`, `test_rag_pipeline.py` | Copilot |
| Architecture Reasoning | `app/architecture_reasoning/` | Architecture explanations | Memory, RAG pipeline pieces | Agents, Planning | `/architecture` (reasoning router) | `test_architecture_reasoning.py` | Copilot |
| Planning Engine | `app/planning/` | Intent → module plan | — | Agents | `/planning` | `test_planning.py` | All agentic flows |
| Multi-Agent Framework | `app/agents/` | Agent registry & collaboration | Planning + engines | `/agents` | `test_agents.py` | New specialist agents |
| Timeline Intelligence | `app/timeline/` | Evolution, hotspots, ownership | Memory, Snapshots, Cache, Telemetry | Planning, Agents, Impact, RAG | `/timeline` | `test_timeline.py` | Git providers |
| Impact Analysis | `app/impact_analysis/` | Change blast radius, propagation, risk, memory refresh hints | GraphQuery, Traverser, SymbolResolver, Memory, Timeline | Planning, Agents, Reports | `/impact` | `test_impact_analysis.py` | PR/diff/CI analysis |
| Engineering Reports | `app/engineering_reports/` | Compose multi-source engineering reports + exporters | Memory, Reasoning, Timeline, Impact, Cache, Telemetry | Copilot, API clients | `/reports` | `test_engineering_reports.py` | PDF/HTML exporters |
| Unified Copilot Orchestrator | `app/copilot/` | Planning-driven orchestration of all intelligence; conversation memory; provider abstraction | Planning, Agents, Memory, RAG, Reasoning, Timeline, Impact, Reports, Cache, Telemetry | Clients / chat UX | `/copilot/chat`, `/execute`, `/history`, legacy `/{id}` | `test_copilot.py` | Cloud LLM providers; specialist agents as tools |

---

## Quality, risk, and design analysis

| Name | Location | Responsibility | API registered? | Public APIs | Related Tests |
|------|----------|----------------|-----------------|-------------|---------------|
| Security | `app/security/` | Security analysis | Yes | `/security` | `test_security_api.py` |
| Metrics | `app/metrics/` | Metrics engine | Yes | `/metrics` | `test_metrics_engine.py` |
| Review | `app/review/` | Code review engine | Yes | `/review` | `test_review_engine.py` |
| Risk | `app/risk/` | Risk scoring | Yes | `/risk` | `test_risk_engine.py` |
| Dependency Health | `app/dependency_health/` | Dependency health | Yes | `/dependency-health` | `test_dependency_health.py` |
| License | `app/license/` | License compliance | Yes | `/license` | `test_license.py` |
| Quality | `app/quality/` | Quality analysis | **No** (router exists) | `/quality` (unwired) | `test_quality_api.py` (failing), `test_quality_analyzer.py`, `test_scoring_engine.py` |
| Smells | `app/smells/` | Smell detection | **No** | `/smells` (unwired) | `test_smells_api.py` (failing), `test_smell_detector.py` |
| Refactoring | `app/refactoring/` | Refactor suggestions | **No** | `/refactoring` (unwired) | `test_refactoring_api.py` (failing), `test_recommendations.py` |
| Architecture Drift | `app/architecture_drift/` | Snapshot drift | Yes | `/architecture-drift` | `test_architecture_drift.py` |
| Architecture Recommendation | `app/architecture_recommendation/` | Recommendations | Yes | `/architecture-recommendation` | `test_architecture_recommendation.py` |
| Design Patterns | `app/design_patterns/` | Pattern detection | Yes | `/design-patterns` | `test_design_patterns.py` |
| SOLID | `app/solid/` | SOLID analysis | Yes | `/solid` | `test_solid.py` |
| Microservices | `app/microservices/` | Boundaries | Yes | `/microservices` | `test_microservices.py` |
| Database Schema | `app/database_schema/` | Schema viz | Yes | `/database-schema` | `test_database_schema.py` |
| API Flow | `app/api_flow/` | API dependency flows | Yes | `/api-flow` | `test_api_flow.py` |
| Architecture Report | `app/architecture_report/` | Reports | Yes | `/architecture-report` | `test_architecture_report.py` |
| Bug Localization | `app/bug_localization/` | Locate bugs | Yes | `/bug-localization` | `test_bug_localization.py` |
| PR Review | `app/pull_request_review/` | PR review | Yes | `/pull-request-review` | `test_pull_request_review.py` |
| Code Generation | `app/code_generation/` | Scaffolding | Yes | `/code-generation` | `test_code_generation.py` |

---

## Product surfaces & integrations

| Name | Location | Responsibility | Public APIs | Related Tests | Notes |
|------|----------|----------------|-------------|---------------|-------|
| Explain | `app/ai/`, `api/explain.py` | Architecture explain | `/explain` | chat/explain related | Uses AI helpers |
| Chat | `app/chat/` | NL chat | `/chat` | `test_chat_*.py` | LLM partially mocked |
| README gen | `app/readme/` | README generation | `/readme` | — | |
| API Docs | `app/apidocs/` | API doc generation | `/apidocs` | `test_apidocs_api.py` | |
| Copilot | `app/copilot/` | Unified Intelligence Orchestrator (CG-070) + legacy capability routing | `/copilot` | `test_copilot.py` | Prefer `/chat` + `/execute` |
| Workspace | `app/workspace/` | Multi-repo workspace | `/workspace` | `test_workspace.py` | |
| Dashboard | `app/dashboard/` | Executive dashboard | `/dashboard` | `test_dashboard.py` | |
| Team Analytics | `app/team_analytics/` | Team metrics | `/team-analytics` | `test_team_analytics.py` | |
| Repository Comparison | `app/repository_comparison/` | Compare repos | `/repository-comparison` | `test_repository_comparison.py` | |
| Release Notes | `app/release_notes/` | Release notes | `/release-notes` | `test_release_notes.py` | |
| GitHub | `app/github/` | GitHub integration | `/github` | `test_github.py` | Mock client |
| CI/CD | `app/cicd/` | Pipeline metadata | `/cicd` | `test_cicd.py` | Mock providers |
| Jira | `app/jira/` | Issue mapping | `/jira` | `test_jira.py` | Mock client |
| Notifications | `app/notifications/` | Slack/Discord | `/notifications` | `test_notifications.py` | Mock clients |

---

## Builtin agents

| Agent | Location | Uses |
|-------|----------|------|
| ArchitectureAgent | `agents/builtin/architecture_agent.py` | Reasoning engine |
| SecurityAgent | `agents/builtin/security_agent.py` | Security domain |
| DocumentationAgent | `agents/builtin/documentation_agent.py` | Memory |
| RefactoringAgent | `agents/builtin/refactoring_agent.py` | Refactoring domain |
| DependencyAgent | `agents/builtin/dependency_agent.py` | Impact (composed) |
| TimelineAgent | `agents/builtin/timeline_agent.py` | Timeline engine |
| ImpactAgent | `agents/builtin/impact_agent.py` | Impact engine |

---

## Documentation package

| Name | Location | Responsibility |
|------|----------|----------------|
| AI_CONTEXT | `/AI_CONTEXT` | Permanent AI knowledge base for all assistants |
