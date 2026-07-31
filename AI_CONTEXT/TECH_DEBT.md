# Technical Debt — CodeGraph

> **Living document.** Update whenever debt is added, mitigated, or discovered.  
> **Related:** [CURRENT_STATUS.md](./CURRENT_STATUS.md) · [ROADMAP.md](./ROADMAP.md)

---

## Known failing tests

**None for RC-1.** Full suite last observed: **1221 passed / 0 failed / 0 skipped**.

Previously failing quality/smells/refactoring API suites were fixed by registering routers in `app/main.py` (RC-1).

---

## Known bugs / gaps

1. **Dual repository roots** — some routers historically used `storage/extracted`, others `uploads`. RC-1 introduced `app/core/paths.resolve_repository_path` for quality/smells/refactoring; remaining upload-based routers should migrate gradually.  
2. **Architecture reasoning vs architecture API** — both use `/architecture` prefix; RC-1 registers reasoning router **before** the generic architecture router.  
3. ~~API registration drift (quality/smells/refactoring)~~ — **resolved in RC-1**.  
4. ~~Root / backend README outdated~~ — **synced in RC-1**.

---

## Mock / stub implementations (by design for RC-1)

| Area | File(s) | Notes |
|------|---------|-------|
| GitHub client | `app/github/github_client.py` | Documented mock |
| Jira client | `app/jira/jira_client.py` | Documented mock |
| CI/CD providers | `app/cicd/provider_client.py` | Documented mock |
| Slack / Discord | `app/notifications/*_client.py` | Documented mocks |
| Chat LLM answers | `app/chat/chat_service.py` | Mock answer generation; prefer Copilot `/chat` |
| Copilot cloud LLM providers | `app/copilot/provider_manager.py` | LocalHeuristic default; Ollama/Azure/Groq stubs |
| Timeline VCS providers | `app/timeline/history_provider.py` | `NotImplementedError` for git/forge providers |
| Code gen templates | `app/code_generation/template_selector.py` | TODO placeholders in templates |
| Report exporters | `app/engineering_reports/exporters.py` | HTML/PDF reserved (`NotImplementedError`) |

---

## Future infrastructure migrations

### Redis (distributed cache)

- Today: `MemoryCache` behind `CacheInterface` / `CacheManager`.  
- Target: Redis implementing `CacheInterface` without changing call sites.

### Vector database

- Embeddings/search/RAG use in-process stores.  
- Target: production vector DB; keep Semantic/RAG facades stable.

### Git integration

- Timeline: real `GitHistoryProvider` / forge providers.  
- Impact: feed PR/diff file lists into `ImpactAnalyzeRequest.related_files`.  
- GitHub engine: replace mock client.

### Kafka / event streaming

- Today: in-process `events` bus.  
- Future: external broker if multi-instance scale requires it.

### Persistence

- Conversation memory, report store, and many registries are process-local.  
- Target: durable stores for multi-instance deployments.

---

## Scalability / performance

- Worker pool + jobs exist; validate under multi-repo load.  
- Timeline/Impact/Report cache TTLs (often 300s) — tune per deployment.  
- Prefer injecting indexed Knowledge Graphs into Impact over lightweight memory-seeded graphs when available.  
- Copilot tool runs may compose several engines — intentional; cache mitigates repeats.

## Security improvements

| Item | RC-1 status |
|------|-------------|
| `EXPOSE_ERROR_DETAILS` (default false) | Added — reasoning API respects it |
| Generic 500 messages on quality/smells/refactoring | Present |
| AuthN/AuthZ | **Not implemented** — open API for RC-1 demo |
| Upload path sandboxing | Relies on upload_id path segments; harden for multi-tenant |
| Secrets | Env-based LLM keys; integration tokens still mock |
| Debug scripts | `debug_chunker*.py` **removed** in RC-1 |

---

## Production readiness limitations (RC-1)

- No authentication / authorization layer  
- In-memory cache, vector store, conversation memory  
- Mock external integrations  
- Single-process assumption for some stores  
- Frontend parity not required for backend RC-1  

These are **documented limitations**, not silent defects.

---

## Documentation debt

- AI_CONTEXT is authoritative for assistants.  
- Human READMEs synced for RC-1; keep them aligned on future CG work.

---

## Debt change log

| Date | Change |
|------|--------|
| 2026-07-31 | Final polish: LICENSE/CONTRIBUTING/CI/PROJECT_ASSETS/docs; removed empty backend stub dirs & manual smoke scripts |
| 2026-07-31 | **RC-1:** registered quality/smells/refactoring; suite 1221/0/0; paths helper; README sync; removed debug_chunker scripts; EXPOSE_ERROR_DETAILS |
| 2026-07-31 | CG-070: Copilot provider stubs; suite tally 1198/18/1 |
| 2026-07-31 | Initial TECH_DEBT from CG-067/068 validation |
