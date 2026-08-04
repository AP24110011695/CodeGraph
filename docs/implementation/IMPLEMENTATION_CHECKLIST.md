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

## Phase 2: Repository Memory Refactoring
- [x] Separate monolithic memory into queryable structured stores
- [x] Implement deterministic memory extractors
  - [x] SymbolTable (functions, classes, constants)
  - [x] ModuleMemory (structural responsibilities, files, public interfaces)
  - [x] WorkflowMemory (structural execution paths, steps)
  - [x] APIMemory (endpoints, methods, handlers)
- [x] Ensure memory is entirely data-driven (no LLM placeholders during index)
- [x] Connect memory injection to Copilot ContextBuilder (kept separate from RAG retrieval)

## Phase 3: Hybrid Retrieval & Context Builder
- [x] Implement deterministic Query Expansion
- [x] Implement lightweight Keyword Retrieval (TF-IDF)
- [x] Implement configurable Hybrid Ranker (Vector + Keyword + Metadata + Memory)
- [x] Implement Context Deduplication and Compression
- [x] Create retrieval evaluation tests and evaluate performance

## Phase 4: Tool Calling & Specialized Analysis
- [x] Audit existing analyzers (QualityAnalyzer, SecurityAnalyzer, ArchitectureBuilder, RepositoryMemory)
- [x] Define standardized ToolResult schema (`tool`, `summary`, `evidence`, `related_files`, `confidence`, `metadata`)
- [x] Implement ToolRegistry with capability-based lookup
- [x] Implement ToolRouter with Intent → Capabilities → Tool(s) mapping
- [x] Implement Architecture Tool (ArchitectureBuilder + DependencyGraph)
- [x] Implement Workflow Tool (WorkflowMemory)
- [x] Implement API Tool (APIMemory)
- [x] Implement Symbol Tool (SymbolTable)
- [x] Implement Quality Tool (QualityAnalyzer)
- [x] Implement Security Tool (SecurityAnalyzer)
- [x] Implement multi-tool orchestration (complex query keyword overrides)
- [x] Extend ToolExecutor.execute_plan() — specialized first, RAG fallback
- [x] Extend ContextBuilder to merge tool_results as structured evidence
- [x] Extend PromptBuilder to render tool evidence as explainable blocks
- [x] 18 Phase 4 tests pass (registry, router, schema, executor, context builder)
- [x] Create TOOL_ROUTING.md documentation

## References
- [Main Documentation](../README.md)
- [Copilot Rebuild Plan](../architecture/COPILOT_REBUILD_PLAN.md)
