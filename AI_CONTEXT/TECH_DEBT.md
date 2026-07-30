# Technical Debt — CodeGraph

> **Living document.** Update whenever debt is added, mitigated, or discovered.  
> **Related:** [CURRENT_STATUS.md](./CURRENT_STATUS.md) · [ROADMAP.md](./ROADMAP.md)

---

## Known failing tests

| Suite | Failures | Root cause |
|-------|----------|------------|
| `tests/test_quality_api.py` | 6 | `app/api/quality.py` not `include_router` in `main.py` → HTTP 404 |
| `tests/test_smells_api.py` | 7 | `app/api/smells.py` not registered → 404 |
| `tests/test_refactoring_api.py` | 5 | `app/api/refactoring.py` not registered → 404 |

**Mitigation:** Register the three routers in `app/main.py` (and resolve any lifecycle/path assumptions in those tests). Domain packages `quality`, `smells`, `refactoring` already exist and are reused elsewhere.

Last observed full-suite tally: **1187 passed / 18 failed / 1 skipped**.

---

## Known bugs / gaps

1. **API registration drift** — quality/smells/refactoring unreachable via HTTP despite tests and routers.  
2. **Root README outdated** — describes planned folders (`backend/api`, `graph`, etc.) that do not match `backend/app/*`.  
3. **Backend README structure** — simplified vs actual multi-package layout.  
4. **Architecture reasoning vs architecture API** — both use `/architecture` prefix in routers; verify route collisions carefully when extending.

---

## Mock / stub implementations (by design today)

| Area | File(s) | Notes |
|------|---------|-------|
| GitHub client | `app/github/github_client.py` | Documented mock |
| Jira client | `app/jira/jira_client.py` | Documented mock |
| CI/CD providers | `app/cicd/provider_client.py` | Documented mock |
| Slack / Discord | `app/notifications/*_client.py` | Documented mocks |
| Chat LLM answers | `app/chat/chat_service.py` | Mock answer generation comments |
| Timeline VCS providers | `app/timeline/history_provider.py` | `NotImplementedError` for git/github/gitlab/bitbucket |
| Code gen templates | `app/code_generation/template_selector.py` | Multiple TODO placeholders in generated templates |

---

## Future infrastructure migrations

### Redis (distributed cache)

- Today: `MemoryCache` behind `CacheInterface` / `CacheManager`.  
- Target: Redis (or similar) implementing `CacheInterface` without changing call sites.

### Vector database

- Embeddings/search/RAG exist with in-process/test-oriented stores.  
- Target: production vector DB; keep Semantic/RAG facades stable.

### Git integration

- Timeline: implement real `GitHistoryProvider` / forge providers.  
- Impact: feed PR/diff file lists into `ImpactAnalyzeRequest.related_files`.  
- GitHub engine: replace mock client with real API.

### Kafka / event streaming

- Today: in-process `events` bus.  
- Future: external broker if multi-instance scale requires it — preserve publish/subscribe semantics.

---

## Scalability / performance

- Worker pool + jobs exist; validate under multi-repo load.  
- Timeline/Impact cache TTLs (300s) — tune per deployment.  
- Full Knowledge Graph builds can be heavy — Impact correctly allows lightweight graphs; prefer injecting indexed KG when available.

## Security improvements

- Replace mock secret/token handling in integration clients with vault-backed credentials.  
- Ensure upload/extraction paths remain sandboxed.  
- Review any debug scripts under `backend/debug_*.py` for leakage in production images.

---

## Documentation debt

- Keep `AI_CONTEXT/` authoritative for AI assistants.  
- Align human READMEs with actual `backend/app` layout when bandwidth allows.

---

## Debt change log

| Date | Change |
|------|--------|
| 2026-07-31 | Initial TECH_DEBT captured from repo inspection + CG-067/068 validation runs |
