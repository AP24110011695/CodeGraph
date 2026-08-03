# Indexing Stall Root Cause Analysis

## Issue 2: Indexing Stalls at EMBEDDING Stage

## Observed Behavior

**Test Results from Local Backend:**
- Upload succeeds
- Auto-indexer starts automatically
- State reaches EMBEDDING at 70% progress
- Index status shows INDEXING
- Total Chunks: 0
- Total Embeddings: 0
- State never progresses beyond EMBEDDING
- Index status never reaches READY
- Indexing appears to hang indefinitely

## Exact Failure Point

**Stuck at**: EMBEDDING stage with 0 chunks and 0 embeddings  
**Auto-indexer State**: Sets state to EMBEDDING (line 90 in auto_indexer.py) before actual embedding  
**Expected Flow**: EMBEDDING → actual embedding generation → READY  
**Actual Flow**: EMBEDDING → [STUCK] → never reaches READY

## Root Cause Analysis

The auto-indexer prematurely sets the repository state to EMBEDDING (70% progress) before the actual embedding generation begins. Then the embedding generation either:

1. Gets stuck during SentenceTransformer model loading
2. Fails silently during embedding generation
3. Has a deadlock or blocking operation
4. The background thread crashes or hangs

**Code Location**: `backend/app/indexing/auto_indexer.py:90`
```python
try:
    state_machine.transition_to(RepositoryStateEnum.EMBEDDING, progress=70, current_stage="Embedding")
except ValueError as e:
    logger.debug("AUTO_INDEXER: Could not transition to EMBEDDING: %s", e)

logger.info("AUTO_INDEXER: Calling create_index for %s", repository_id)
# Trigger indexing
index = self.index_manager.create_index(project_path, repository_id, force=False)
```

The state is set to EMBEDDING BEFORE `create_index()` is called, but `create_index()` includes the actual embedding generation which may be failing silently.

## Proposed Fix

The auto-indexer should not manually set states during the indexing process. The state transitions should be handled by the incremental indexer or the job system, not by the auto-indexer itself.

**Solution**: Remove manual state transitions from auto-indexer and let the actual indexing process handle state transitions properly.