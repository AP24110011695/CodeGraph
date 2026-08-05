# INDEXING_PIPELINE_FLOW.md

### CodeGraph — Indexing Pipeline Flow

_Derived from SYSTEM_ARCHITECTURE.md and DATA_FLOW.md._

---

## 1. Overview
The Indexing Pipeline runs at index-time (once per repository or incrementally on file change). It produces the Vector Store and the 11 Repository Memory artifacts.

## 2. Pipeline Stages

1. **Repository Scanner**: Walks the repo tree, classifies files by role (entrypoint, service, model, test, config, util), and builds the directory/file graph. Output: File manifest with role tags.
2. **Metadata Extraction**: Extracts per-file exports/imports and one-line summaries. Output: File metadata records.
3. **Chunker**: Splits source into syntax-aware chunks at function/class boundaries via tree-sitter, preserving parent linkage. Output: Chunk records with parent pointers.
4. **Embedding**: Generates vector representations at chunk-level and summary-level using a code-aware embedding model.
5. **Vector Store Persistence**: Persists chunk vectors with filterable metadata (file, symbol, role, lines).
6. **Repository Memory Builder**: Constructs 11 independent memory stores (8 deterministic via static extraction, 3 interpretive via LLM summarization).

## 3. Data Contract (Chunk Record)
```json
{
  "chunk_id": "string",
  "file": "string",
  "symbol": "string | null",
  "symbol_kind": "function | class | method | module | null",
  "module": "string",
  "lines": "[start, end]",
  "role": "entrypoint | service | model | test | config | util",
  "parent_chunk_id": "string | null",
  "vector": "float[]",
  "text": "string"
}
```

## 4. References
- [Data Flow](../architecture/DATA_FLOW.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
