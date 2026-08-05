# CONTEXT_ASSEMBLY.md

### CodeGraph — Context Assembly

_Derived from RAG_PIPELINE.md and DATA_FLOW.md._

---

## 1. Overview
The Context Builder normalizes chunks (from retrieval and from deterministic tools) into one attributed schema, deduplicates them, orders them, and prioritizes them to fit under the LLM context budget before sending to the Prompt Builder.

## 2. Deduplication and Ranking
- **Deduplication key**: `(file, line_range)` overlap.
- **Ranking order**:
  - Default: Reranker score, descending.
  - `workflow_tracing` / `api_tracing`: Execution order from Graph Explorer.
  - Metadata-match boost: Direct entity matches are pinned above pure-semantic matches.

## 3. Context Prioritization Under Budget
When assembling context exceeds the usable window, truncation follows a strict priority order:
1. Chunks with direct entity match.
2. Chunks on the resolved execution/dependency path.
3. Highest-reranked remaining semantic matches.
4. Summary-level memory as a fallback for omitted items.

If truncation occurs, an explicit marker is added so the Prompt Builder can instruct the model not to imply completeness.

## 4. Output Schema (To Prompt Builder)
```json
{
  "file": "string",
  "function": "string | null",
  "class": "string | null",
  "module": "string",
  "lines": "[start, end]",
  "reason_selected": "string",
  "code": "string",
  "relationship_to_question": "string"
}
```

## 5. References
- [RAG Pipeline](../architecture/RAG_PIPELINE.md)
- [Prompt Pipeline](../architecture/PROMPT_PIPELINE.md)
