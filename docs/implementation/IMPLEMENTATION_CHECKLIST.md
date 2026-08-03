# Implementation Checklist

## Phase 0: Stabilization
- [x] Remove fake / placeholder data from application
  - [x] Repository metadata (files, folders, sizes)
  - [x] Indexing progress and remaining time estimates
  - [x] Dashboard analytics and scores
  - [x] Copilot demo responses and hardcoded text
- [x] Implement explicit "unavailable" states instead of 0 or misleading defaults
- [x] Ensure backend tests pass with "unavailable" states and data-driven structures
- [x] Verify dashboard stability

## Phase 1: Orchestration Layer & Intent Routing
- [x] Audit current Copilot pipeline and document findings
- [x] Implement deterministic Phase 1 intent routing (`file_lookup`, `code_explanation`, `workflow`, `architecture`, `bug_analysis`, `general_query`)
- [x] Restructure RAG context assembly — FILE/SYMBOL/REASON/CODE blocks instead of raw concatenation
- [x] Rebuild Prompt Builder with intent-specific output format templates
- [x] Remove generic response sections ("Analysis Results", "Key Findings", "Recommendations")
- [x] Implement lightweight intent-based answer verification in PostProcessor
- [x] Update CopilotEngine to normalize legacy intents to Phase 1 equivalents
- [x] Remove hardcoded scores from legacy `_build_repository_data` path
- [x] All 50 copilot tests pass; all 1,231 backend tests pass

## Phase 2: Repository Memory Refactoring (Future)
- [ ] Separate monolithic memory into queryable structured stores
- [ ] Implement deterministic memory extractors

## Phase 3: Hybrid Retrieval & Context Builder (Future)
- [ ] Implement Hybrid Search (BM25 + Vector)
- [ ] Implement Context Builder with attribution rules

## Phase 4: Prompt Builder & Output Verification (Future)
- [ ] Implement strict per-intent Prompt Builder
- [ ] Implement closed-loop Answer Verification with retry

## References
- [Main Documentation](../README.md)
- [Copilot Rebuild Plan](../architecture/COPILOT_REBUILD_PLAN.md)
