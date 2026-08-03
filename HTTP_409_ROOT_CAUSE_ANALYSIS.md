# HTTP 409 Root Cause Analysis

## Exact Endpoint Returning HTTP 409

**Endpoint**: `POST /index/{upload_id}`
**Backend File**: `backend/app/api/indexing.py`
**Line Number**: 39
**Exception**: `IndexAlreadyExistsError("Repository indexing is already in progress")`

## Complete Stack Trace

1. **Frontend Upload Flow**:
   - User uploads ZIP → Backend extracts repository
   - Backend publishes `REPOSITORY_UPLOADED` event
   - Auto-indexer receives event and starts background indexing

2. **Auto-indexer Background Flow**:
   - `backend/app/indexing/auto_indexer.py:96` - Calls `index_manager.create_index(project_path, repository_id, force=False)`
   - `backend/app/indexing/index_manager.py:66-74` - Sets index status to `INDEXING`

3. **Frontend Polling Flow**:
   - Frontend navigates to `/indexing/{uploadId}`
   - `frontend/src/features/indexing/api/indexing.queries.ts:124` - Calls `startMutation.mutate()`
   - `frontend/src/features/indexing/api/indexing.api.ts:13-21` - POST to `/index/{upload_id}`

4. **Backend Response**:
   - `backend/app/api/indexing.py:34-39` - `create_index()` endpoint
   - `backend/app/indexing/index_manager.py:68-70` - Checks if status is `INDEXING`
   - `backend/app/indexing/index_manager.py:70` - Raises `IndexAlreadyExistsError`
   - `backend/app/api/indexing.py:39` - Returns HTTP 409

## Why Backend Thinks Request is Conflict

**Root Cause**: Race condition between auto-indexer and frontend manual indexing request

**Sequence of Events**:
1. Upload completes successfully
2. Auto-indexer starts background thread and calls `create_index()`
3. Auto-indexer sets index status to `INDEXING` (line 73 in index_manager.py)
4. Frontend calls POST `/index/{upload_id}` to start indexing
5. Backend checks existing index status (line 68 in index_manager.py)
6. Backend finds status is `INDEXING` (from auto-indexer)
7. Backend raises `IndexAlreadyExistsError` (line 70 in index_manager.py)
8. Backend returns HTTP 409 (line 39 in indexing.py)

**Specific Code Location**:
```python
# backend/app/indexing/index_manager.py:66-70
def create_index(self, project_path: Path, upload_id: str, force: bool = False) -> RepositoryIndex:
    """Create an index, or replace its vectors when force is requested."""
    existing = self.get_index(upload_id)
    if existing and existing.status == IndexStatus.INDEXING:  # LINE 69
        raise IndexAlreadyExistsError("Repository indexing is already in progress")  # LINE 70
```

## Repository State Verification

**Before Auto-indexer**:
- State: `UPLOADED`
- Index Status: `NOT_INDEXED` or null

**After Auto-indexer Starts**:
- State: `EMBEDDING` (line 90 in auto_indexer.py)
- Index Status: `INDEXING` (line 73 in index_manager.py)

**After Frontend POST Request**:
- State: Still `EMBEDDING` (auto-indexer still running)
- Index Status: Still `INDEXING` (from auto-indexer)
- Backend Response: HTTP 409

## Database Contents

**Index Table** (via SQLite in repository_store):
- `upload_id`: The repository ID
- `status`: `INDEXING` (set by auto-indexer)
- `indexed_at`: null (not complete yet)
- `error`: null

**Repository State Table**:
- `repository`: The repository ID
- `state`: `EMBEDDING` (set by auto-indexer)
- `progress`: 70%
- `current_stage`: "Embedding"

## Vector Store Contents

**Before HTTP 409**:
- Empty or partially populated (depending on when auto-indexer was interrupted)

**After HTTP 409**:
- Same state - no change since request was rejected

## Embedding Generation

**Auto-indexer Context**:
- Auto-indexer calls `create_index()` in background thread
- Embedding generation happens inside `IncrementalIndexer.index()`
- When frontend gets 409, auto-indexer may still be generating embeddings
- Or auto-indexer may have completed but didn't update state to READY

## Polling Endpoints

**Frontend Polls**:
1. `GET /index/{upload_id}` - Returns index status
2. `GET /repository-state/{upload_id}` - Returns repository state

**Polling Logic**:
- `frontend/src/features/indexing/api/indexing.queries.ts:128-133` - Treats 409 as warning, keeps polling
- Frontend expects status to eventually become `READY`
- But auto-indexer may have already finished or may be stuck

## Frontend Polling Logic

**Problem**: Frontend treats 409 as "already in progress, keep polling" but auto-indexer controls the actual indexing

**Code Location**:
```typescript
// frontend/src/features/indexing/api/indexing.queries.ts:128-133
onError: (error) => {
  const message = isAPIError(error) ? error.message : 'Failed to start indexing';
  // 409 = already exists / in progress — keep polling.
  if (isAPIError(error) && error.status === 409) {
    setEvents((prev) => pushEvent(prev, message, 'warning'));
    return;  // Keeps polling instead of treating as error
  }
  setEvents((prev) => pushEvent(prev, message, 'error'));
  setIndexingStatus('error');
},
```

## Why READY is Never Reached

**Root Cause**: Dual indexing initiation system creates race condition

**Scenario 1: Auto-indexer Completes Successfully**
- Auto-indexer finishes embedding generation
- Auto-indexer sets state to READY (line 103 in auto_indexer.py)
- Frontend eventually sees READY in polling
- **This should work** - but user reports it doesn't reach READY

**Scenario 2: Auto-indexer Fails Silently**
- Auto-indexer encounters error during embedding
- Auto-indexer transitions to FAILED (line 114 in auto_indexer.py)
- Frontend keeps polling expecting READY
- **User would see FAILED state** - but user reports HTTP 409

**Scenario 3: Auto-indexer Gets Stuck**
- Auto-indexer gets stuck during embedding generation
- State remains EMBEDDING, index status remains INDEXING
- Frontend keeps polling indefinitely
- **This matches user's report** - never reaches READY

**Most Likely Cause**: Auto-indexer gets stuck during embedding generation, leaving state as EMBEDDING/Indexing but never completing.

## Proposed Fix

**Option 1: Disable Auto-indexer for Manual Flow**
- Remove auto-indexer subscription or make it conditional
- Let frontend control indexing entirely
- Frontend calls POST /index when ready

**Option 2: Frontend Should Not Call POST /index**
- Frontend should detect if auto-indexer is already running
- If auto-indexer started, frontend should only poll GET endpoints
- Remove POST /index call from frontend logic

**Option 3: Backend Should Allow Reentrant Indexing**
- Remove 409 check or make it more permissive
- Allow multiple indexing requests
- Let last request determine final state

**Option 4: Unified Indexing Control**
- Either auto-indexer OR frontend should control indexing
- Not both simultaneously
- Add a flag to disable auto-indexer for manual uploads

**Recommended Fix**: Option 2 - Frontend should detect if auto-indexer is already running and only poll GET endpoints, removing the redundant POST /index call that causes the 409.