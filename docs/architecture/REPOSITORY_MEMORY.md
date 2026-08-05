# REPOSITORY_MEMORY.md

### CodeGraph — Repository Memory Architecture

_Derived from COPILOT_REBUILD_PLAN.md and SYSTEM_ARCHITECTURE.md._

---

## 1. Overview
Repository Memory consists of 11 structured artifacts built at index-time. They are independently built and independently queryable stores — never concatenated into a single document injected by default.

## 2. Memory Types

### Deterministic Memories (Built via static extraction)
- **Route Memory**: Built via AST pattern match on route-registration calls. Used for workflow/API tracing.
- **API Memory**: External API client call sites matched via AST against known SDK/client call patterns.
- **Dependency Memory**: AST-based import graph.
- **Call Graph Memory**: Tree-sitter call resolution, cross-file via Symbol Table.
- **Workflow Memory**: Precomputed Call Graph traversal from entrypoints.
- **Symbol Table**: Tree-sitter extraction (name, file, lines, kind, signature).
- **Configuration Memory**: AST/pattern match on config keys, definitions, and consumption sites.
- **Database Schema Memory**: Parse model classes/migration DDL into schema structure.

### Interpretive Memories (Built via scoped LLM summarization)
- **Architecture Memory**: Bottom-up LLM summarization over module memories, validated against actual directory/import structure.
- **Module Memory**: LLM summary from constituent file summaries.
- **File Memory**: One-line LLM summary per file content.

## 3. Usage
These memories are persisted and queried by the Tool Router and Hybrid Retrieval stages at Query-Time.

## 4. References
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Data Flow](DATA_FLOW.md)
