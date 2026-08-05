# Indexing Runtime Report

**Date:** 2026-08-06  
**Repository:** trace_test_repo.zip (simple Python files)  
**upload_id:** 7f476c91-5e00-415c-8800-ada5d38e29d9

## Timeline

**Stage 1: API Endpoint**  
POST /repositories/{repository_id}/index  
Status: PASS  
Duration: ~0.1s

**Stage 2: Repository Validation**  
Status: PASS  
Duration: ~0.01s

**Stage 3: Scanner**  
Status: PASS  
Duration: ~0.5s  
Files scanned: 3

**Stage 4: Parser**  
Status: PASS  
Duration: ~0.5s  
Files parsed: 3

**Stage 5: Chunk Generation**  
Status: PASS  
Duration: ~0.1s  
Chunks generated: 2

**Stage 6: Embedding Generation**  
Status: FAIL  
Duration: 106.69s  
Embeddings generated: 0

**Stage 7: Vector Store Insertion**  
Status: SKIPPED (no embeddings)  
Duration: N/A

**Stage 8: Repository State Transition**  
Status: PASS  
Duration: ~0.1s  
Final state: READY

**Stage 9: READY Event**  
Status: PASS  
Duration: ~0.01s

## First Failing Stage

**Stage:** Embedding Generation  
**Function:** `SentenceTransformerProvider._get_model()`  
**File:** `app/rag/embedding_service.py`  
**Line:** 174

## Runtime Evidence

```
[TRACE] _embed_documents called with 2 chunks
[TRACE] _embed_documents completed in 106.69s, returned 0 documents
```

**Backend Logs:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
EMBEDDING_SERVICE: Failed to load SentenceTransformer model: The paging file is too small for this operation to complete. (os error 1455)
```

**Stack Trace:**
```
File "C:\Projects\CodeGraph\backend\app\rag\embedding_service.py", line 174, in _get_model
    model = SentenceTransformer(self.model_name)
OSError: The paging file is too small for this operation to complete. (os error 1455)
```

**Cascading Failures:**
```
app.rag.embedding_service.EmbeddingError: Sentence-transformers embedding error: The paging file is too small for this operation to complete. (os error 1455)
Skipping chunk with failed embedding: main.py:functions:1-1
app.rag.embedding_service.EmbeddingError: Embedding generation failed: Sentence-transformers embedding error: The paging file is too small for this operation to complete. (os error 1455)
```

## Current State

**Repository Status:** READY  
**Total Chunks:** 0  
**Total Embeddings:** 0  
**Progress:** 100%

## Last Successful Stage

Chunk Generation - 2 chunks were successfully generated from 3 files.

## Next Stage Never Reached

Vector Store Insertion - No embeddings were generated, so nothing could be stored in the vector store.

## Root Cause

**Exact Cause:** Windows virtual memory (paging file) is too small to load the SentenceTransformer model (all-MiniLM-L6-v2, ~120MB model + dependencies).

**Technical Details:**
- The SentenceTransformer model loading requires significant memory
- Windows OS error 1455 indicates insufficient paging file space
- The model loading fails during `SentenceTransformer(self.model_name)` initialization
- This causes all embedding generation to fail
- The pipeline gracefully handles the failure by skipping chunks
- The repository still transitions to READY state but with 0 embeddings
- This makes search, memory, and dashboard non-functional

## Verification

✓ Chunk generation actually finishes - YES (2 chunks generated)  
✓ Every chunk is processed - YES (both chunks attempted embedding)  
✓ Embedding model loads successfully - NO (paging file error)  
✓ Embeddings are generated - NO (model load failure)  
✓ Vector store insertion completes - SKIPPED (no embeddings)  
✓ Index is persisted - YES (with 0 documents)  
✓ Repository state transition executes - YES (to READY)  
✓ READY state is reached - YES (but with no data)  
✓ READY event is published - YES

## Backend Logs Summary

```
INCREMENTAL_INDEXER: Starting indexing for 7f476c91-5e00-415c-8800-ada5d38e29d9 (force=True)
INCREMENTAL_INDEXER: Step 0 - Clearing analysis cache
INCREMENTAL_INDEXER: Step 1 - Scanning project
INCREMENTAL_INDEXER: Step 1 complete - Scanned 3 files
INCREMENTAL_INDEXER: Step 2 - Computing repository snapshot
INCREMENTAL_INDEXER: Step 2 complete - Snapshot computed
INCREMENTAL_INDEXER: Step 3 - Force rebuild requested
INCREMENTAL_INDEXER: Step 3 complete - Force rebuild cleanup done
INCREMENTAL_INDEXER: Step 4 - First-time indexing - 3 files to add
INCREMENTAL_INDEXER: Step 5 - No vectors to delete
INCREMENTAL_INDEXER: Step 6 - Indexing 3 files
INCREMENTAL_INDEXER: Step 6.1 - Running pipeline on 3 files
INDEXING_PIPELINE: Indexing 3 files for 7f476c91-5e00-415c-8800-ada5d38e29d9
INDEXING_PIPELINE: Step 1 - Detecting frameworks
INDEXING_PIPELINE: Step 1 complete - Frameworks detected
INDEXING_PIPELINE: Step 2 - Parsing 3 files
INDEXING_PIPELINE: Step 2 complete - Parsed 3 files
INDEXING_PIPELINE: Step 3 - Chunking files
INDEXING_PIPELINE: Step 3 complete - Generated 2 chunks from 3 files
INDEXING_PIPELINE: Step 4 - Generating embeddings for 2 chunks
EMBEDDING_SERVICE: Failed to load SentenceTransformer model: The paging file is too small for this operation to complete. (os error 1455)
INDEXING_PIPELINE: Step 4 complete - Generated 0 embeddings from 2 chunks
INDEXING_PIPELINE: File indexing complete for 7f476c91-5e00-415c-8800-ada5d38e29d9 - chunks: 0, embeddings: 0
```

## Conclusion

The indexing pipeline DOES complete and reach the READY state, but it fails to generate any embeddings due to insufficient Windows virtual memory. The repository is marked as READY with 0 chunks and 0 embeddings, making it functionally useless for search, memory, and dashboard operations.

**First Runtime Failure Point:** `app/rag/embedding_service.py:174` in `SentenceTransformerProvider._get_model()`  
**Exact Error:** `OSError: The paging file is too small for this operation to complete. (os error 1455)`  
**Impact:** No embeddings can be generated, rendering the indexed repository non-functional

---

## Minimum Code Change Required

**Option 1:** Increase Windows virtual memory/paging file size (system configuration, not code change)

**Option 2:** Use a smaller embedding model or provider that requires less memory

**Option 3:** Add better error handling to fail the indexing process when embeddings cannot be generated, rather than silently continuing with 0 embeddings

**Option 4:** Add a fallback to a mock embedding provider for development/testing when real embeddings cannot be generated

**Recommended:** Option 3 - Add proper error handling to fail indexing when embedding generation fails completely, so the repository status accurately reflects that it is not ready for use.