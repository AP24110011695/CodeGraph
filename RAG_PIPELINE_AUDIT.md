# RAG Pipeline Audit Report

## Issue 3: Copilot Hallucination - RAG Pipeline Analysis

## RAG Pipeline Components

### 1. Repository Ready Check
**File**: `backend/app/chat/chat_service.py:72-76`
```python
index = self.index_manager.get_index(upload_id)
if not index:
    raise ChatServiceError(f"Repository {upload_id} is not indexed")
if index.status != IndexStatus.READY:
    raise ChatServiceError(f"Repository {upload_id} index is not ready (status: {index.status})")
```

**Verification**: Chat service correctly checks if repository is indexed and ready before proceeding.

### 2. Retrieval Process
**File**: `backend/app/chat/chat_service.py:88-96`
```python
retrieved_chunks = self.retriever.retrieve(
    query=message,
    upload_id=upload_id,
    top_k=5,
)
```

**Verification**: Retriever is called with the upload_id to filter results.

### 3. Empty Results Handling
**File**: `backend/app/chat/chat_service.py:99-114`
```python
if not retrieved_chunks:
    answer = "I could not find enough evidence in this repository."
    sources = []
    confidence = 0.0
    tokens_used = 0
```

**Verification**: When no chunks are retrieved, a generic response is returned.

### 4. Vector Store Search
**File**: `backend/app/rag/retriever.py:73-77`
```python
results = self.vector_store.search(
    query_embedding=query_embedding,
    top_k=top_k,
    filters=filters,
)
```

**Verification**: Vector store is searched with the query embedding and upload_id filter.

### 5. Root Cause of Hallucination

**Primary Issue**: Due to Issue 2 (indexing stalls at EMBEDDING), repositories never reach READY state. Therefore:

1. Chat service rejects requests with "Repository is not ready (status: INDEXING)"
2. Even if repositories were READY, the vector store would be empty (0 chunks, 0 embeddings) due to indexing stall
3. With empty vector store, retriever returns 0 chunks
4. Chat service returns generic "I could not find enough evidence" message
5. This appears as "hallucination" but is actually missing data

## Verification Counts

**From Indexing Trace**:
- Total Chunks: 0
- Total Embeddings: 0
- Index Status: INDEXING (never reaches READY)
- Repository State: EMBEDDING (stuck)

**Expected State for Working RAG**:
- Total Chunks: > 0
- Total Embeddings: > 0
- Index Status: READY
- Repository State: READY
- Vector Store: Populated with documents

## Conclusion

The RAG pipeline is correctly implemented. The "hallucination" issue is caused by the indexing stall (Issue 2) which prevents repositories from being properly indexed and populated with embeddings. Once Issue 2 is fixed, the RAG pipeline should work correctly.

## Proposed Fix

Fix Issue 2 (indexing stall) first, which will resolve the RAG pipeline issue as a side effect. The RAG pipeline itself is not broken - it just lacks indexed data to work with.