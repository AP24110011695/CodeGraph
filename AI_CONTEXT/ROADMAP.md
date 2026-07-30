# Roadmap — CodeGraph

> **Living document.** Update after every completed CG module.  
> **Related:** [CURRENT_STATUS.md](./CURRENT_STATUS.md) · [CHANGELOG_AI.md](./CHANGELOG_AI.md) · [MODULE_INDEX.md](./MODULE_INDEX.md)

---

## How to read this roadmap

- **CG-001 … CG-066** — Treated as **implemented** foundation (ingest → intelligence stack through Multi-Agent Framework), per project operating assumption and presence of corresponding packages/routers.
- **CG-067** — Timeline Intelligence — **completed**.
- **CG-068** — Impact Analysis — **completed**.
- **CG-069** — Engineering Intelligence Report Generator — **completed** (current latest).
- **CG-070+** — Not specified in-repo; do not invent ticket titles.

---

## Current phase

| Field | Value |
|-------|-------|
| **Phase** | Intelligence Platform — Composed Reporting |
| **Current module** | CG-069 complete; awaiting next assigned CG ticket |
| **Latest milestone** | Engineering Intelligence Report Generator |

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

### Wave E — Temporal & predictive (latest)

| CG | Module | Status |
|----|--------|--------|
| CG-067 | Repository Timeline Intelligence | **Done** |
| CG-068 | Intelligent Code Impact Analysis | **Done** (dependency/architecture/API/propagation/risk/confidence; affected modules/services/APIs/symbols/memory; Git/PR-ready `related_files`) |
| CG-069 | Engineering Intelligence Report Generator | **Done** (composed reports; pluggable exporters JSON/Markdown; HTML/PDF stubs) |

---

## Overall completion (approximate)

| Area | Status |
|------|--------|
| Core analysis engines | Present and registered (except quality/smells/refactoring **API** wiring) |
| Platform (cache, telemetry, workflows, workers) | Present |
| Planning + Agents | Present (7 builtin agents) |
| Timeline + Impact + Reports | Present |
| Production VCS/LLM/Redis/Vector | Stubbed / in-memory / mock — see debt |
| Frontend parity | Partial / separate tree |

**Rough backend capability completion:** high for in-process enterprise demo architecture; **production hardening** still open.

---

## Upcoming modules

> Assign concrete CG-069+ titles only when product tickets exist.

Candidate themes **already hinted by stubs/extension points** (not committed tickets):

1. Real History Providers (Git/GitHub/GitLab/Bitbucket) for Timeline  
2. Diff/PR-driven Impact Analysis (consume `related_files`)  
3. Redis `CacheInterface` backend  
4. Production vector DB for Semantic/RAG  
5. Register quality/smells/refactoring routers + fix 18 tests  
6. Real LLM client for Chat/Explain  
7. Event streaming (Kafka-class) replacing pure in-process bus if scale requires  

---

## Architecture milestones

- [x] Unified Knowledge Graph + GraphQuery  
- [x] Repository Memory facade  
- [x] Planning → Agents pipeline  
- [x] Provider-style Timeline history abstraction  
- [x] Impact analysis reusing traverser (no duplicate BFS)  
- [ ] Production distributed cache  
- [ ] Production embedding store  
- [ ] Live VCS providers  

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
