# Roadmap — CodeGraph

> **Living document.** Update after every completed CG module.  
> **Related:** [CURRENT_STATUS.md](./CURRENT_STATUS.md) · [CHANGELOG_AI.md](./CHANGELOG_AI.md) · [MODULE_INDEX.md](./MODULE_INDEX.md)

---

## How to read this roadmap

- **CG-001 … CG-066** — Treated as **implemented** foundation (ingest → intelligence stack through Multi-Agent Framework), per project operating assumption and presence of corresponding packages/routers.
- **CG-067** — Timeline Intelligence — **completed**.
- **CG-068** — Impact Analysis — **completed**.
- **CG-069** — Engineering Intelligence Report Generator — **completed**.
- **CG-070** — Unified Intelligence Orchestrator (CodeGraph Copilot) — **completed**.
- **RC-1** — Release Candidate 1 stabilization — **completed** (current latest).
- **CG-071+ / GA** — Not specified in-repo; do not invent ticket titles.

---

## Current phase

| Field | Value |
|-------|-------|
| **Phase** | Portfolio-ready Release Candidate 1 |
| **Current module** | Final polish complete |
| **Latest milestone** | GitHub + PROJECT_ASSETS + docs packaging |
| **Version** | `1.0.0-rc.1` |

---

## Completed capability waves (mapped to repo reality)

### Wave A — Ingest & structure

Upload, Scanner, Framework detection, Parser, Dependency Graph, Architecture builder, Diagrams/UML, Indexing.

### Wave B — Quality & governance

Security, Metrics, Review, Knowledge Graph, Risk, Dependency Health, License, Architecture Drift, Recommendations, Bug Localization, PR Review, Code Generation, Design Patterns, SOLID, Microservices, Database Schema, API Flow, Architecture Report.

### Wave C — Collaboration & ops surface

Workspace, GitHub, CI/CD, Jira, Notifications, Team Analytics, Repository Comparison, Release Notes, Dashboard, Copilot, Jobs, Repository State, Events, Workflows, Workers, Reliability.

### Wave D — Platform intelligence core

Incremental Indexing / Snapshots, Distributed Cache, Telemetry, Semantic Engine, Repository Memory, Advanced RAG, Architecture Reasoning, Planning Engine, Multi-Agent Framework.

### Wave E — Temporal & predictive

| CG | Module | Status |
|----|--------|--------|
| CG-067 | Repository Timeline Intelligence | **Done** |
| CG-068 | Intelligent Code Impact Analysis | **Done** (dependency/architecture/API/propagation/risk/confidence; affected modules/services/APIs/symbols/memory; Git/PR-ready `related_files`) |
| CG-069 | Engineering Intelligence Report Generator | **Done** (composed reports; pluggable exporters JSON/Markdown; HTML/PDF stubs) |

### Wave F — Unified orchestration

| CG | Module | Status |
|----|--------|--------|
| CG-070 | Unified Intelligence Orchestrator (CodeGraph Copilot) | **Done** |

### Wave G — Release Candidate (latest)

| Milestone | Status |
|-----------|--------|
| RC-1 regression stabilization (0 failing tests) | **Done** |
| Quality / Smells / Refactoring API registration | **Done** |
| README + AI_CONTEXT sync | **Done** |
| Shared repository path helper | **Done** |
| Production limitation documentation | **Done** |

---

## Overall completion (approximate)

| Area | Status |
|------|--------|
| Core analysis engines | Present and **registered** (incl. quality/smells/refactoring) |
| Platform (cache, telemetry, workflows, workers) | Present |
| Planning + Agents | Present (7 builtin agents) |
| Timeline + Impact + Reports + Copilot | Present |
| Regression suite | **Green** (1221 passed) |
| Production VCS/LLM/Redis/Vector/Auth | Stubbed / in-memory / mock — see debt |
| Frontend parity | Partial / separate tree |

**Backend RC-1:** ready as an in-process enterprise intelligence demo with a green suite. **GA** still needs auth, durable stores, and live integrations.

---

## Upcoming modules

> Assign concrete post-RC titles only when product tickets exist.

Candidate themes (not committed tickets):

1. Authentication / API keys / multi-tenant isolation  
2. Real History Providers (Git/GitHub/GitLab/Bitbucket) for Timeline  
3. Diff/PR-driven Impact Analysis  
4. Redis `CacheInterface` backend + durable conversation/report stores  
5. Production vector DB for Semantic/RAG  
6. Wire cloud LLM providers for Copilot synthesis  
7. Migrate remaining routers to `resolve_repository_path`  
8. Event streaming if multi-instance scale requires it  

---

## Architecture milestones

- [x] Unified Knowledge Graph + GraphQuery  
- [x] Repository Memory facade  
- [x] Planning → Agents pipeline  
- [x] Provider-style Timeline history abstraction  
- [x] Impact analysis reusing traverser (no duplicate BFS)  
- [x] Unified Copilot Orchestrator composing all intelligence  
- [x] RC-1 green suite + registered quality/smells/refactoring APIs  
- [ ] Production distributed cache  
- [ ] Production embedding store  
- [ ] Live VCS providers  
- [ ] Authentication / authorization  

## Technical milestones

- [x] Telemetry middleware + facade  
- [x] Workflow DAG `repository_processing`  
- [x] Incremental snapshot evolution  
- [ ] Eliminate mock integration clients (GitHub/Jira/CI/Slack/Discord)  
- [ ] Close API registration gaps  

---

## Update checklist (after each CG)

1. Move ticket from upcoming → completed table.  
2. Adjust **Current phase / module**.  
3. Sync [CURRENT_STATUS.md](./CURRENT_STATUS.md) and [CHANGELOG_AI.md](./CHANGELOG_AI.md).  
4. Add module row to [MODULE_INDEX.md](./MODULE_INDEX.md).  
5. Append [LESSONS_LEARNED.md](./LESSONS_LEARNED.md).
