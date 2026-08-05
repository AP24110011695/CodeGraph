# Root Cause Analysis: Empty Symbol Table in Copilot

## Executive Summary

The Copilot pipeline is working correctly, but the repository indexing and memory building systems are **disconnected**. Parsing results are generated during indexing but **not persisted**, and repository memory is **not automatically built** after indexing completes. When Copilot needs memory, it triggers on-demand memory building which re-parses the repository, but this parsing often fails or returns empty results.

## Complete Execution Flow Analysis

### 1. Upload API → Indexing Flow

```
POST /upload
├── upload_service.save_upload()
├── extraction_service.extract()
├── repository_store.register_upload()
└── event_bus.publish(REPOSITORY_UPLOADED)
    ↓
    ↓ [Event]
    ↓
AutoIndexer.on_repository_uploaded()
├── index_manager.create_index()
    ↓
    ↓
    ↓
IndexManager.create_index()
├── IncrementalIndexer.index()
    ↓
    ↓
    ↓
IncrementalIndexer.index()
├── pipeline.scanner.scan()
├── RepositorySnapshot.compute()
├── pipeline.index_files()
    ├── IndexingPipeline.index_files()
    │   ├── detector.detect()
    │   ├── ParserEngine.parse_project() ← **PARSING HAPPENS HERE**
    │   ├── chunker.chunk_file()
    │   ├── embedding_service.embed()
    │   └── vector_store.add()
    └── RepositorySnapshot.save()
└── RepositoryStateMachine.transition_to(READY)
```

**Key Finding**: Parsing results are generated in `IndexingPipeline.index_files()` but **only used for chunking and embedding**. They are **not saved** anywhere.

### 2. Copilot Query Flow

```
POST /copilot/chat
├── CopilotEngine.chat()
├── QueryPlanner.plan_query()
├── ToolExecutor.execute_plan()
├── ContextBuilder.build()
    ├── needs_memory = True (from query plan)
    ├── cache.get(copilot_context)
    ├── memory_engine.get_memory_summary() → None
    ├── memory_engine.build_memory() ← **MEMORY BUILT ON-DEMAND**
        ↓
        ↓
        ↓
        MemoryEngine.build_memory()
        ├── MemoryBuilder.build()
        │   ├── resolve_indexed_project_path()
        │   ├── scanner_service.scan()
        │   ├── ParserEngine.parse_project() ← **PARSING HAPPENS AGAIN**
        │   ├── detector_service.detect()
        │   ├── graph_builder.build()
        │   ├── architecture_builder.build()
        │   ├── symbol_table_extractor.extract()
        │   ├── module_memory_extractor.extract()
        │   ├── api_memory_extractor.extract()
        │   └── workflow_memory_extractor.extract()
        └── memory_store.set()
    └── context assembly
├── PromptBuilder.build()
├── ProviderManager.generate()
└── PostProcessor.process()
```

**Key Finding**: Memory is built **on-demand** when Copilot needs it, not automatically after indexing. This triggers a **second parsing** of the repository.

### 3. Where Parsing Data Disappears

#### Stage 1: Indexing Pipeline (First Parsing)
**File**: `app/indexing/indexing_pipeline.py`
**Function**: `IndexingPipeline.index_files()`
**Line**: 141
```python
parsing = ParserEngine.parse_project(project_path, subset_scan)
parsed_by_path = {result.path: result for result in parsing.files}
```

**What happens**:
- Parsing succeeds
- Results used for chunking (line 163: `parsed_by_path.get(file_info.path)`)
- **Results are NOT saved anywhere**
- **Results are discarded after chunking**

#### Stage 2: Memory Builder (Second Parsing)
**File**: `app/repository_memory/memory_builder.py`
**Function**: `MemoryBuilder.build()`
**Line**: 38
```python
parsing_result = ParserEngine.parse_project(project_path, scan_result)
```

**What happens**:
- Parsing is called again
- If parsing fails or returns empty, symbols are empty
- Results used for symbol extraction (line 44)
- Results stored in in-memory `MemoryStore`

#### Stage 3: Symbol Table Extraction
**File**: `app/repository_memory/symbol_table_extractor.py`
**Function**: `SymbolTableExtractor.extract()`
**Line**: 11
```python
if not parsing_result or not parsing_result.files:
    return symbols  # Returns empty dict
```

**What happens**:
- If parsing_result is None or has no files, returns empty symbols
- This is the **first location where symbols become 0**

## Root Causes

### Root Cause #1: No Persistence of Parsing Results

**Problem**: Parsing results are generated during indexing but not persisted.

**Evidence**:
- `IndexingPipeline.index_files()` calls `ParserEngine.parse_project()` (line 141)
- Results are used only for chunking and embedding
- No code saves parsing results to disk or database
- No code retrieves saved parsing results

**Impact**: 
- Every component that needs parsing results must re-parse
- Re-parsing is expensive and can fail
- No consistency guarantee between indexing and memory building

**Responsible Code**:
- `app/indexing/indexing_pipeline.py:141` - Parsing happens but not saved
- `app/indexing/indexing_pipeline.py:163` - Parsing used for chunking only

### Root Cause #2: No Automatic Memory Building After Indexing

**Problem**: Repository memory is not automatically built after indexing completes.

**Evidence**:
- `AutoIndexer` only subscribes to `REPOSITORY_UPLOADED` event
- No subscriber for `REPOSITORY_READY` event to trigger memory building
- Memory is built on-demand in `ContextBuilder.build()` (line 84)
- On-demand building happens during Copilot queries, not after indexing

**Impact**:
- Memory is built during query time, adding latency
- If memory building fails, query fails
- No pre-verification that memory can be built successfully

**Responsible Code**:
- `app/main.py:87` - Only subscribes auto-indexer to `REPOSITORY_UPLOADED`
- `app/copilot/context_builder.py:84` - On-demand memory building
- Missing: Subscriber for `REPOSITORY_READY` event

### Root Cause #3: In-Memory Only Memory Storage

**Problem**: Repository memory is stored in-memory only, not persisted.

**Evidence**:
- `MemoryStore` uses `dict[str, RepositoryMemory]` (line 7)
- No persistence to disk or database
- Memory is lost on server restart
- Each server instance has its own memory

**Impact**:
- Memory must be rebuilt after server restart
- No consistency across multiple server instances
- High memory usage for large repositories

**Responsible Code**:
- `app/repository_memory/memory_store.py:7` - In-memory storage only
- No persistence layer implementation

### Root Cause #4: Parsing Failure in Memory Builder

**Problem**: Second parsing in MemoryBuilder often fails or returns empty results.

**Evidence**:
- MemoryBuilder calls `ParserEngine.parse_project()` independently
- No reuse of parsing results from indexing
- Parsing can fail due to:
  - File system issues
  - Language support limitations
  - Encoding issues
  - Timeouts
  - Cache invalidation issues

**Impact**:
- If parsing fails, symbol extraction gets empty results
- Copilot receives 0 symbols
- LLM responds with "not enough analyzed repository information"

**Responsible Code**:
- `app/repository_memory/memory_builder.py:38` - Re-parsing without reuse
- `app/parsers/parser_engine.py:22` - No caching of parsing results

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Upload & Indexing Flow                       │
└─────────────────────────────────────────────────────────────────┘

Upload → Extract → Register → Event → AutoIndexer → IndexManager
                                                              │
                                                        IncrementalIndexer
                                                              │
                                                        IndexingPipeline
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   ParserEngine   │
                                                    │   parse_project  │ ← **PARSING #1**
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   Chunker        │
                                                    │   (uses parsing) │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   Embedding      │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   Vector Store   │
                                                    │   (persisted)    │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   State Machine  │
                                                    │   (READY)        │
                                                    └─────────┬─────────┘
                                                              │
                                                              ❌ **NO MEMORY BUILDING**
                                                              ❌ **NO PARSING PERSISTENCE**
                                                              ❌ **NO MEMORY PERSISTENCE**

┌─────────────────────────────────────────────────────────────────┐
│                        Copilot Query Flow                         │
└─────────────────────────────────────────────────────────────────┘

Query → CopilotEngine → QueryPlanner → ToolExecutor → ContextBuilder
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   Memory Check   │
                                                    │   (not in cache) │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   MemoryEngine   │
                                                    │   build_memory   │ ← **ON-DEMAND**
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   MemoryBuilder  │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   ParserEngine   │
                                                    │   parse_project  │ ← **PARSING #2**
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   (may fail)     │
                                                    │   (may be empty) │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   SymbolExtract  │
                                                    │   (empty if      │
                                                    │    parsing fails)│
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   MemoryStore    │
                                                    │   (in-memory)    │
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   Context        │
                                                    │   (empty symbols)│
                                                    └─────────┬─────────┘
                                                              │
                                                    ┌─────────┴─────────┐
                                                    │   LLM Response   │
                                                    │   "not enough    │
                                                    │    information"  │
                                                    └─────────────────┘
```

## First Location Where Data Disappears

**Location**: `app/indexing/indexing_pipeline.py:141`

**Function**: `IndexingPipeline.index_files()`

**Event**: 
```python
parsing = ParserEngine.parse_project(project_path, subset_scan)
parsed_by_path = {result.path: result for result in parsing.files}
```

**Why Data Disappears**:
- Parsing results are generated successfully
- Results are used for chunking (line 163)
- After chunking, results are **not saved anywhere**
- Results are **discarded** when function returns

**Next Location**: `app/repository_memory/memory_builder.py:38`

**Function**: `MemoryBuilder.build()`

**Event**:
```python
parsing_result = ParserEngine.parse_project(project_path, scan_result)
```

**Why Data Disappears**:
- New parsing attempt (no reuse of previous results)
- If this parsing fails or returns empty, downstream components get no data
- No fallback to previously generated parsing results

## Recommended Fixes

### Fix #1: Persist Parsing Results During Indexing

**Priority**: HIGH

**Implementation**:
1. Add parsing result persistence to `IndexingPipeline.index_files()`
2. Save parsing results to disk or database after successful parsing
3. Include parsing result path in `RepositoryIndex` metadata
4. Modify `MemoryBuilder` to check for saved parsing results first

**Files to Modify**:
- `app/indexing/indexing_pipeline.py` - Save parsing results
- `app/indexing/indexing_models.py` - Add parsing_result_path field
- `app/repository_memory/memory_builder.py` - Load saved parsing results
- `storage/repository_store.py` - Persist parsing result metadata

### Fix #2: Trigger Memory Building After Indexing

**Priority**: HIGH

**Implementation**:
1. Create subscriber for `REPOSITORY_READY` event
2. Trigger `memory_engine.build_memory()` in subscriber
3. Handle memory building failures gracefully
4. Update repository state to reflect memory status

**Files to Modify**:
- `app/main.py` - Register memory builder subscriber
- Create `app/repository_memory/auto_memory_builder.py` - New subscriber
- `app/repository_state/state_machine.py` - Add memory states

### Fix #3: Persist Repository Memory

**Priority**: MEDIUM

**Implementation**:
1. Replace in-memory `MemoryStore` with persistent storage
2. Use SQLite or PostgreSQL for memory persistence
3. Serialize/deserialize `RepositoryMemory` objects
4. Add memory loading on server startup

**Files to Modify**:
- `app/repository_memory/memory_store.py` - Add persistence layer
- `storage/database.py` - Add memory tables
- `app/repository_memory/memory_serializer.py` - Serialize/deserialize

### Fix #4: Add Parsing Result Caching

**Priority**: MEDIUM

**Implementation**:
1. Extend `analysis_cache.py` to cache parsing results
2. Use cache key based on repository ID and file hash
3. Set appropriate TTL for parsing cache
4. Clear cache on repository updates

**Files to Modify**:
- `app/cache/analysis_cache.py` - Add parsing cache
- `app/parsers/parser_engine.py` - Use cache in parse_project
- `app/indexing/incremental_indexer.py` - Clear cache on updates

### Fix #5: Add Memory Building Status Tracking

**Priority**: LOW

**Implementation**:
1. Add memory status to repository state machine
2. Track memory build success/failure
3. Display memory status in UI
4. Allow manual memory rebuild

**Files to Modify**:
- `app/repository_state/state_machine.py` - Add memory states
- `app/schemas/repository_state.py` - Add memory status enum
- Frontend - Display memory status

## Verification Steps

1. After implementing Fix #1, verify parsing results are saved during indexing
2. After implementing Fix #2, verify memory is built automatically after indexing
3. After implementing Fix #3, verify memory persists across server restarts
4. After implementing Fix #4, verify cached parsing results are reused
5. Test complete flow: Upload → Index → Memory Build → Copilot Query

## Conclusion

The root cause is a **disconnect between indexing and memory building**. The indexing pipeline generates parsing results but doesn't persist them, and memory building is not automatically triggered after indexing. When Copilot needs memory, it triggers on-demand memory building which re-parses the repository, but this re-parsing often fails or returns empty results, leading to 0 symbols and the "not enough analyzed repository information" response.

The fix requires:
1. **Persisting parsing results** during indexing
2. **Automatically building memory** after indexing completes
3. **Persisting repository memory** for reuse
4. **Caching parsing results** to avoid re-parsing
5. **Tracking memory build status** for monitoring

These fixes will ensure that parsing results are preserved and reused, memory is built automatically after indexing, and Copilot has access to the analyzed repository information it needs.
