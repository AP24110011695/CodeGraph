# RAG_PIPELINE.md

### CodeGraph — Retrieval-Augmented Generation Pipeline

_Derived from COPILOT_REBUILD_PLAN.md. Scope: everything between "repository content exists" and "an attributed context payload is ready for the Prompt Builder." Intent classification, prompt templates, tool implementations, and verification are covered in SYSTEM_ARCHITECTURE.md / COPILOT_REBUILD_PLAN.md, not here._

---

## 1. Purpose and Scope

The RAG pipeline is responsible for one thing: given a query and its classified intent, produce a ranked, deduplicated, fully-attributed set of evidence chunks — and know when _not_ to rely on similarity search at all. It does not decide the answer's wording or structure; that is the Prompt Builder's job. It does not classify intent; that is the Intent Router's job. It consumes the Query Planner's execution plan as input.

The pipeline is intentionally not a single fixed strategy. It branches by intent: some questions are lookup problems better solved by exact symbol match, some are multi-hop problems requiring graph traversal, and only the remainder are genuinely best served by semantic similarity search. Treating every query as a similarity-search problem was the retrieval-side contributor to CodeGraph's original generic-answer symptom, and this pipeline is designed specifically to avoid that default.

---

## 2. Pipeline Stages

```
Query + Execution Plan (from Query Planner)
    ↓
Retrieval Strategy Selection   (symbol_table_lookup / hybrid_semantic /
                                 graph_traversal / schema_lookup)
    ↓
   ┌─────────────┬──────────────────┬───────────────────┐
   ↓             ↓                  ↓                    ↓
Symbol Table   Hybrid Search    Graph Traversal      Schema Lookup
Lookup         (BM25 + Vector)  (Call Graph /         (DB Schema
                                 Route Memory)          Memory)
   ↓             ↓                  ↓                    ↓
   └─────────────┴──────────────────┴───────────────────┘
                          ↓
              Metadata Filtering (role/module)
                          ↓
              Parent Document Expansion
                          ↓
              Cross-Encoder Reranking
                          ↓
              Deduplication (by file+lines identity)
                          ↓
              Chunk Ranking / Ordering
              (relevance-descending, or execution-order
               for workflow_tracing / api_tracing)
                          ↓
              Context Prioritization
              (fit to context budget)
                          ↓
              Context Builder Output → Prompt Builder
```

---

## 3. Retrieval Strategy Selection

The Query Planner's execution plan specifies one primary `retrieval_strategy`. This pipeline does not re-derive strategy — it executes what the plan specifies.

| Strategy              | When Selected                                                                                                       | What Runs                                                                                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `symbol_table_lookup` | `file_lookup`, direct-symbol `code_explanation`, `configuration`                                                    | Exact/fuzzy match against Symbol Table; semantic search only as a secondary, clearly-labeled fallback if no symbol match                                                                       |
| `hybrid_semantic`     | `code_explanation` (non-symbol), `bug_finding`, `refactoring`, `security_review`, `testing`, `performance_analysis` | Full hybrid search pipeline (§4)                                                                                                                                                               |
| `graph_traversal`     | `workflow_tracing`, `api_tracing`, `dependency_tracing`                                                             | Call Graph / Route Memory / Dependency Memory traversal from a resolved entrypoint or entity; hybrid search runs only to _locate_ the starting entrypoint, not to answer the question directly |
| `schema_lookup`       | `database_query`                                                                                                    | Direct query against Database Schema Memory; hybrid search supplements with the actual query/ORM code chunks                                                                                   |

For multi-intent queries (§9 of the rebuild plan), each sub-intent's strategy runs independently against the shared entity set, and their outputs are merged at the Context Builder stage.

---

## 4. Hybrid Search

### 4.1 Components

- **BM25 index** — built over chunk text at index time; catches exact identifier matches (function names, API names, string literals) that vector similarity frequently under-ranks.
- **Vector search** — over the Vector Store's chunk-level and summary-level embeddings.
- **Merge:** both candidate sets are combined (union, not intersection) before any filtering or reranking — an item in only one list is still a valid candidate.

### 4.2 Metadata Filtering

Applied after merge, before reranking. Filters (not strict excludes, but rank boosts/demotions) candidates by role tag (entrypoint/service/model/test/config/util) and module, when the classified intent implies a target layer — e.g., an `api_tracing` query about an external SDK call biases toward `service`-role files.

### 4.3 Parent Document Retrieval

Matching happens at chunk granularity (function/method-level, from tree-sitter chunking) for precision. Once a chunk matches, its parent (enclosing class or file) is fetched alongside it so the returned evidence isn't structurally truncated — this specifically addresses the case where a function's signature and body would otherwise be split across a fixed-size chunk boundary; tree-sitter chunking already avoids the split, but parent expansion additionally restores surrounding class/file context when it matters for the question.

### 4.4 Cross-Encoder Reranking

Applied to the merged, filtered candidate set. A cross-encoder scores (query, chunk) pairs directly, which is more precise than the bi-encoder similarity used for initial vector search — this is what determines final top-k selection before deduplication.

---

## 5. Graph Retrieval

Not a default strategy — invoked specifically when `retrieval_strategy = graph_traversal`.

- **Entrypoint resolution:** the execution plan's `entrypoint_hint` (e.g., "route matching /upload in Route Memory") is resolved via Route Finder or Symbol Lookup first.
- **Traversal:** Graph Explorer walks Call Graph Memory from the resolved entrypoint, N hops or until an exit/external boundary (e.g., a third-party SDK call, a database write) is reached.
- **Caching:** for common paths, Workflow Memory stores a precomputed traversal so repeated workflow questions skip live graph walking.
- **Output shape:** an ordered sequence of (file, function, lines) steps — this ordering is preserved through Context Builder rather than being re-sorted by relevance score.

Graph retrieval is the only strategy that produces execution-ordered (not relevance-ordered) output, and Context Builder must be told which mode it's receiving so it doesn't re-rank a trace into similarity order.

---

## 6. Query Decomposition (Multi-Hop Queries)

For intents that are inherently multi-hop (`workflow_tracing`, `architecture`, `dependency_tracing`), the Query Planner has already decomposed the query into an ordered list of sub-targets (e.g., "PDF upload workflow" → frontend handler → API route → parser → embedding call → vector store write) before this pipeline runs. Each sub-target gets its own retrieval pass — effectively multi-query retrieval, but scoped and ordered by the decomposition rather than generated as free-form query variants. This pipeline does not implement generic query expansion as a separate mechanism; the decomposition from the Query Planner is treated as the expansion step.

---

## 7. Deduplication and Ranking

- **Deduplication key:** `(file, line_range)` overlap. If hybrid search and graph traversal both surface the same function, it is merged into one chunk record with a combined `reason_selected` field rather than appearing twice.
- **Ranking order:**
  - Default: reranker score, descending.
  - `workflow_tracing` / `api_tracing`: execution order from Graph Explorer, overriding relevance score entirely.
- **Metadata-match boost:** chunks with a direct entity match (exact symbol/API name from the query's extracted entities) are pinned above pure-semantic matches regardless of reranker score.

---

## 8. Context Prioritization Under Budget

When assembled context would exceed the model's usable context window, truncation follows a fixed priority order — never a silent drop of the highest-value evidence:

1. Chunks with direct entity match (symbol/API name match against extracted entities).
2. Chunks on the resolved execution/dependency path for the classified intent.
3. Highest-reranked remaining semantic matches.
4. Summary-level memory (module/file summaries) as a fallback for anything cut.

If truncation occurs, the Context Builder output includes an explicit marker (e.g., "N additional lower-relevance matches omitted") so the Prompt Builder can instruct the model not to imply completeness it doesn't have.

---

## 9. What's Implemented vs. Deliberately Excluded

| Technique                     | Status                                      | Rationale                                                                                                                                                                 |
| ----------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hybrid Search (BM25 + Vector) | Implemented                                 | Exact-identifier recall that vector-only search misses                                                                                                                    |
| Metadata Filtering            | Implemented                                 | Structural signal (role/module) narrows candidates for layer-specific questions                                                                                           |
| Parent Document Retrieval     | Implemented                                 | Restores structural completeness around a matched chunk                                                                                                                   |
| Cross-Encoder Reranking       | Implemented                                 | Precision improvement on the merged candidate set at low marginal cost                                                                                                    |
| Graph Retrieval               | Implemented, intent-gated                   | Required specifically for multi-hop workflow/dependency/API questions; not run by default                                                                                 |
| Query Decomposition           | Implemented (via Query Planner)             | Handles multi-hop intents without a separate generic-expansion system                                                                                                     |
| Multi-Query Retrieval         | Implemented as a byproduct of decomposition | Not built as an independent, always-on mechanism                                                                                                                          |
| Generic Query Expansion       | Not implemented separately                  | Subsumed by Query Planner decomposition; building both is redundant                                                                                                       |
| Contextual Compression        | Not implemented                             | No measured context-overflow problem yet; adds an LLM call, cost, latency, and a new hallucination surface — revisit only if truncation (§8) becomes frequent in practice |

---

## 10. Chunk Record Schema (input to this pipeline, from the Vector Store)

```
{
  chunk_id: string,
  file: string,
  symbol: string | null,
  symbol_kind: "function" | "class" | "method" | "module" | null,
  module: string,
  lines: [start: int, end: int],
  role: "entrypoint" | "service" | "model" | "test" | "config" | "util",
  parent_chunk_id: string | null,
  vector: float[],
  text: string
}
```

## 11. Context Builder Output Schema (output of this pipeline, to the Prompt Builder)

```
{
  file: string,
  function: string | null,
  class: string | null,
  module: string,
  lines: [int, int],
  reason_selected: string,
  code: string,
  relationship_to_question: string
}
```

Every record leaving this pipeline carries `reason_selected` and `relationship_to_question` regardless of which retrieval strategy produced it (symbol lookup, hybrid search, or graph traversal) — this uniform attribution is what allows the Prompt Builder to cite evidence consistently no matter which path the query took to get there.

---

_End of RAG_PIPELINE.md._
