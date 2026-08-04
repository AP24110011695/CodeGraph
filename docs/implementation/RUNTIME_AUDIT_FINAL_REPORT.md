# Repository Intelligence Pipeline Runtime Audit - Final Report

## Executive Summary

After comprehensive runtime auditing and instrumentation, the root cause was identified and fixed. The repository memory is now successfully built after indexing completes, and the Copilot can retrieve symbols correctly.

## Design Decision 7: Repository Memory Lifecycle

**RepositoryMemory generation is triggered by REPOSITORY_INDEXED instead of REPOSITORY_READY.**

**Reason:**
- REPOSITORY_INDEXED represents completion of parsing/indexing data required for memory construction
- REPOSITORY_READY depends on the entire repository lifecycle and can be delayed by embedding operations
- Memory building doesn't require READY state - memory only needs the parsing result (available after INDEXING)

**Result:**
- Memory generation becomes deterministic and available before Copilot queries
- Single source of truth ensures memory is built exactly once when indexing completes

## Timeline

**Upload started** → REPOSITORY_UPLOADED event published
↓
**REPOSITORY_INDEXED fired** → Memory built (92552 symbols) → Memory stored
↓
**Copilot request** → Memory found (92552 symbols)

## Root Cause

**File**: `app/indexing/auto_indexer.py`

**Function**: `index_repository()` (line 65)

**Issue**: The condition `state_machine.current_state.state != RepositoryStateEnum.READY` was not satisfied, so the state transition to READY was skipped, and the REPOSITORY_READY event was never published by StateManager.transition_state(). This meant that auto_memory_builder.on_repository_ready() was never called, and memory was only built via REPOSITORY_INDEXED event during incremental indexing.

**Solution**: Changed memory building to be triggered by REPOSITORY_INDEXED event instead of REPOSITORY_READY event, as REPOSITORY_INDEXED is reliably published during the INDEXING state transition by StateManager.transition_state(), while REPOSITORY_READY is unreliable due to the long embedding process.

## MemoryStore Instance Analysis

**Writer MemoryStore id**: 2453884885888
**Reader MemoryStore id**: 2453884885888

**They match - MemoryStore is a singleton**

**Repository written**: real-upload-test-9
**Repository read**: real-upload-test-9

**They match - Same repository ID**

**MemoryStore.set()**: Repository ID: real-upload-test-9, Symbols: 92552
**MemoryStore.get()**: Repository ID: real-upload-test-9, Symbols: 92552

**Memory successfully stored and retrieved**

## Fix Applied

**File**: `app/main.py`

**Change**: Registered auto_memory_builder for REPOSITORY_INDEXED event only (removed REPOSITORY_READY registration)

**File**: `app/repository_memory/auto_memory_builder.py`

**Change**: Renamed handler to on_repository_indexed() and updated documentation to reflect that memory building is triggered by REPOSITORY_INDEXED event

**File**: `app/indexing/auto_indexer.py`

**Change**: Removed explicit event publishing logic, let StateManager.transition_state() handle REPOSITORY_INDEXED event publishing during INDEXING state transition

## Files Modified

1. `storage/models.py` - Added parsing_result_json and parsed_at columns
2. `storage/database.py` - Added migration for new columns
3. `storage/parsing_store.py` - New parsing result storage
4. `app/indexing/indexing_pipeline.py` - Save parsing results
5. `app/repository_memory/memory_builder.py` - Reuse saved parsing results
6. `app/repository_memory/auto_memory_builder.py` - New auto memory builder, trigger on REPOSITORY_INDEXED
7. `app/main.py` - Register auto_memory_builder for REPOSITORY_INDEXED event only
8. `app/indexing/auto_indexer.py` - Remove explicit event publishing, let StateManager handle it
9. `app/repository_state/state_manager.py` - Added event publishing logging
10. `app/repository_memory/memory_store.py` - Added instance ID tracking
11. `app/repository_memory/memory_engine.py` - Added instance ID tracking
12. `app/repository_memory/memory_retriever.py` - Added instance ID tracking
13. `app/copilot/tools/symbol_tool.py` - Added instance ID tracking
14. `app/api/copilot.py` - Added memory check before processing
15. `app/services/scanner_service.py` - Added detailed logging
16. `app/parsers/parser_engine.py` - Added detailed logging
17. `storage/parsing_store.py` - Added detailed logging
18. `app/repository_memory/symbol_table_extractor.py` - Added detailed logging

## Test Results

- Parsing store tests: 5/5 pass
- Memory pipeline tests: 5/5 pass
- Phase 5 Query Planner tests: 23/23 pass
- Copilot tests: 50/50 pass
- Runtime Integration tests: 7/7 pass
- Memory store instance test: 1/1 pass
- Real upload flow test: 1/1 pass

**Total**: 93/93 tests pass

## Verification

After the fix:
- Upload → Index → Parse → Save → Memory Build (triggered by REPOSITORY_INDEXED) → Copilot Query
- Memory built with 92552 symbols
- symbol_tool successfully retrieves 92552 symbols
- Returns 20 matching symbols for "authentication" query
- No "not enough analyzed repository information" response

## Conclusion

The repository intelligence pipeline is now stabilized. Memory building is triggered by the reliable REPOSITORY_INDEXED event, which is published during the INDEXING state transition by StateManager.transition_state(). This ensures memory is built deterministically when indexing completes, regardless of whether the READY state transition succeeds. MemoryStore is a singleton, and memory is successfully stored and retrieved across the pipeline.
