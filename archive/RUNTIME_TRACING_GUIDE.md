# Runtime Tracing Guide - Actual Frontend Request

This document explains how to trace the actual frontend request to identify why a READY repository returns 0 symbols, 0 evidence, and 0 RAG chunks.

## Tracing Setup

### 1. Enhanced Logging Added

The following components now have detailed runtime tracing:

**Frontend API Entry Point** (`app/api/copilot.py`):
- Logs incoming repository_id from frontend
- Logs query, conversation_id, provider
- Logs chat completion status

**Repository Path Resolution** (`app/indexing/repository_access.py`):
- Logs upload_id resolution process
- Logs store type and project path resolution
- Logs validation of project path existence and directory status

**Repository Store** (`storage/repository_store.py`):
- Logs database row lookup for upload_id
- Logs extraction_path, repository_id, status, indexing_state
- Logs candidate path validation
- Logs filesystem fallback process

**Symbol Table Extraction** (`app/repository_memory/symbol_table_extractor.py`):
- Logs parsing result availability
- Logs file count and symbol extraction process
- Logs total symbols extracted with type breakdown

**Copilot Engine** (`app/copilot/copilot_engine.py`):
- Logs complete execution pipeline with 11 stages
- Logs tool execution results and evidence counts
- Logs repository memory and RAG context availability
- Logs complete prompts and LLM responses

### 2. How to Trace

1. **Start the backend server**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Open the frontend and select a repository**
   - Ensure the repository shows as "READY" in the UI
   - Note the repository_id in the UI (it might be different from the upload_id)

3. **Make a copilot query**
   - Ask: "Where is authentication implemented?"
   - Note the exact query text

4. **Check the backend logs**
   - Look for "FRONTEND COPILOT CHAT REQUEST" section
   - Look for "REPOSITORY PATH RESOLUTION" section
   - Look for "REPOSITORY STORE PATH RESOLUTION" section
   - Look for "SYMBOL TABLE EXTRACTION" section
   - Look for the complete 11-stage pipeline trace

### 3. Key Points to Check

#### A. Repository ID Matching
```
FRONTEND COPILOT CHAT REQUEST
Repository ID from frontend: <frontend_id>
```

vs

```
REPOSITORY PATH RESOLUTION
Upload ID: <resolved_id>
```

**Question**: Do these match? If not, the repository_id is being overwritten somewhere.

#### B. Repository Path Resolution
```
REPOSITORY STORE PATH RESOLUTION
Database row found: True/False
Row extraction_path: <path>
Row status: <status>
Row indexing_state: <state>
✓ Using DB path: <path>
```

**Question**: Is the repository status "READY"? If not, the repository isn't indexed.

#### C. Symbol Table Extraction
```
SYMBOL TABLE EXTRACTION
Repository ID: <id>
Parsing result available: True/False
Files available for parsing: <count>
Total symbols extracted: <count>
Symbol types breakdown:
  class: <count>
  function: <count>
  interface: <count>
  enum: <count>
  variable: <count>
```

**Question**: Are symbols being extracted? If 0, the parsing or extraction is failing.

#### D. Tool Execution
```
TOOL EXECUTION
Tool 1: symbol_tool
  Status: ok
  Summary: Symbol table contains 0 symbol(s)
  Evidence items: 0
  Related files: 0
  Confidence: 0.30
```

**Question**: Is the tool returning 0 evidence? If yes, the memory is empty.

#### E. Repository Memory
```
REPOSITORY MEMORY
Memory summary available: <class>
  Memory keys: ['repository_id', 'repository_summary', 'architecture_summary', 'module_count', 'file_count', 'symbol_count']
```

**Question**: What are the actual counts? Are they 0?

### 4. Expected Flow for a READY Repository

For a properly indexed repository, you should see:

1. **Frontend Request**: repository_id matches a known upload_id
2. **Path Resolution**: Database row found with status=READY, valid path returned
3. **Symbol Extraction**: Files available for parsing > 0, total symbols extracted > 0
4. **Tool Execution**: Evidence items > 0, related files > 0, confidence > 0.5
5. **Repository Memory**: symbol_count > 0, file_count > 0, module_count > 0
6. **RAG Context**: RAG citations count > 0
7. **LLM Response**: Actual answer with evidence, not "not enough information"

### 5. Common Issues

#### Issue 1: Repository ID Mismatch
**Symptom**: Frontend sends one repository_id, but backend resolves a different one
**Check**: Compare "Repository ID from frontend" vs "Upload ID" in path resolution
**Possible Cause**: Frontend is using display name instead of upload_id

#### Issue 2: Repository Not Ready
**Symptom**: Database row shows status != READY
**Check**: "Row indexing_state" in repository store logs
**Solution**: Repository needs to be indexed first

#### Issue 3: Path Resolution Failure
**Symptom**: "Project path not found" or path doesn't exist
**Check**: "Row extraction_path" and filesystem fallback
**Solution**: Repository path is missing or incorrect in database

#### Issue 4: Empty Symbol Table
**Symptom**: "Total symbols extracted: 0"
**Check**: "Files available for parsing" and "Parsing result available"
**Solution**: Parsing is failing or returning empty results

#### Issue 5: Tool Returns Empty Evidence
**Symptom**: Tool runs successfully but returns 0 evidence items
**Check**: Symbol table counts in memory summary
**Solution**: Memory building is not extracting symbols correctly

### 6. Example of Good Flow

```
FRONTEND COPILOT CHAT REQUEST
Repository ID from frontend: abc123-def456
Query: Where is authentication implemented?

REPOSITORY PATH RESOLUTION
Upload ID: abc123-def456
✓ Using DB path: C:\Projects\CodeGraph\extracted\abc123-def456

REPOSITORY STORE PATH RESOLUTION
Database row found: True
Row indexing_state: READY
✓ Using DB path: C:\Projects\CodeGraph\extracted\abc123-def456

SYMBOL TABLE EXTRACTION
Repository ID: abc123-def456
Files available for parsing: 45
Total symbols extracted: 234
Symbol types breakdown:
  class: 45
  function: 167
  interface: 12
  enum: 8
  variable: 2

TOOL EXECUTION
Tool 1: symbol_tool
  Status: ok
  Summary: Symbol table contains 234 symbol(s). Found 3 matching symbol(s) for query.
  Evidence items: 3
  Related files: 2
  Confidence: 0.95

REPOSITORY MEMORY
  symbol_count: 234
  file_count: 45
  module_count: 8

RAG CONTEXT
RAG citations count: 5

LLM RESPONSE
**Location**: src/auth/authenticate.py
**Symbol**: authenticate_user
**Purpose**: Authenticates user credentials
...
```

### 7. Next Steps

Run the tracing with your actual frontend request and identify the first stage where the data becomes 0 or missing. The logging will show exactly where the pipeline breaks down.
