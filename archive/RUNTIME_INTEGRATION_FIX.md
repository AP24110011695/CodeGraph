# Runtime Integration Fix - Phase 5 Tool Name Mismatch

**Issue**: Query Planner requested tools with PascalCase names (e.g., `SymbolTool`) but Tool Registry registered tools with snake_case names (e.g., `symbol_tool`), causing tool resolution failures.

**Root Cause**: Naming convention mismatch between Query Planner and Tool Registry.

---

## 1. Problem Analysis

### 1.1 Execution Path Trace

```
IntentRouter
  → Classifies intent (e.g., "file_lookup")
  → Returns intent to CopilotEngine

QueryPlanner (Phase 5)
  → Creates execution plan
  → WRONG: Requests "SymbolTool" (PascalCase)
  → Passes plan to ToolExecutor

ToolExecutor
  → Extracts required_tools from plan
  → Looks up "SymbolTool" in ToolRegistry
  → FAILS: ToolRegistry only has "symbol_tool" (snake_case)
  → Logs: "PHASE5: Tool SymbolTool not found in registry"
  → Falls back to RAG

ToolRegistry
  → Registered tools: symbol_tool, architecture_tool, workflow_tool, etc.
  → All names are snake_case
```

### 1.2 Naming Mismatch

| Component | Tool Names Used | Format |
|-----------|----------------|--------|
| **Tool Registry** (registration) | `symbol_tool`, `architecture_tool`, `workflow_tool`, `api_tool`, `security_tool`, `quality_tool` | snake_case |
| **Query Planner** (requests) | `SymbolTool`, `ArchitectureTool`, `WorkflowTool`, `APITool`, `SecurityTool`, `QualityTool` | PascalCase |
| **Phase 5 Specification** | Referenced as "SymbolTool", "ArchitectureTool", etc. | PascalCase |

---

## 2. Solution

### 2.1 Fix Applied

**Changed Query Planner to use snake_case tool names** to match Tool Registry registration.

**File Modified**: `backend/app/copilot/query_planner.py`

**Changes**:
1. Updated `_INTENT_TOOLS` mapping to use snake_case names
2. Updated `_select_tools()` method to use snake_case names in overrides

### 2.2 Code Changes

#### Before (PascalCase - WRONG):
```python
_INTENT_TOOLS: Dict[str, List[str]] = {
    "file_lookup": ["SymbolTool"],
    "code_explanation": ["SymbolTool"],
    "workflow": ["WorkflowTool"],
    "architecture": ["ArchitectureTool"],
    "api_flow": ["APITool"],
    "quality_analysis": ["QualityTool"],
    "security_analysis": ["SecurityTool"],
    "bug_analysis": ["SecurityTool", "SymbolTool"],
    "general_query": [],
}
```

#### After (snake_case - CORRECT):
```python
_INTENT_TOOLS: Dict[str, List[str]] = {
    "file_lookup": ["symbol_tool"],
    "code_explanation": ["symbol_tool"],
    "workflow": ["workflow_tool"],
    "architecture": ["architecture_tool"],
    "api_flow": ["api_tool"],
    "quality_analysis": ["quality_tool"],
    "security_analysis": ["security_tool"],
    "bug_analysis": ["security_tool", "symbol_tool"],
    "general_query": [],
}
```

### 2.3 Enhanced Logging

**File Modified**: `backend/app/copilot/tool_executor.py`

**Change**: Enhanced error logging to show available tools when a tool is not found.

```python
logger.error("PHASE5: Tool %s not found in registry - available tools: %s", 
             tool_name, [t.name for t in tool_registry.list_tools()])
```

This helps debug future registration issues by showing what tools are actually available.

---

## 3. Test Updates

### 3.1 Updated Phase 5 Tests

**File Modified**: `backend/tests/test_phase5_query_planner.py`

Updated all test assertions to use snake_case tool names:
- `SymbolTool` → `symbol_tool`
- `ArchitectureTool` → `architecture_tool`
- `WorkflowTool` → `workflow_tool`
- `APITool` → `api_tool`
- `SecurityTool` → `security_tool`

### 3.2 New Runtime Integration Test

**File Created**: `backend/tests/test_runtime_integration.py`

Added comprehensive runtime integration tests to verify:
1. All Phase 4 tools are registered
2. Query Planner tool names match Tool Registry names
3. Specific queries resolve to correct tools:
   - "Where is authentication implemented?" → `symbol_tool`
   - "Explain upload workflow" → `workflow_tool`
   - "Explain architecture" → `architecture_tool`
   - "Find security issues" → `security_tool`
4. Tool Executor can resolve all planned tools
5. All tool names follow snake_case convention

---

## 4. Verification

### 4.1 Test Results

All tests pass after the fix:

```
tests/test_phase4_tools.py: 18 passed
tests/test_phase5_query_planner.py: 23 passed
tests/test_runtime_integration.py: 7 passed
tests/test_copilot.py: 50 passed
tests/test_copilot_intent_routing.py: 2 passed

Total: 100 copilot/tool-related tests passed
```

### 4.2 Query Verification

| Query | Expected Tool | Tool Found | Status |
|-------|--------------|------------|--------|
| "Where is authentication implemented?" | `symbol_tool` | ✅ Found | PASS |
| "Explain upload workflow" | `workflow_tool` | ✅ Found | PASS |
| "Explain architecture" | `architecture_tool` | ✅ Found | PASS |
| "Find security issues" | `security_tool` | ✅ Found | PASS |

### 4.3 Tool Registration Verification

All Phase 4 tools are correctly registered:
- ✅ `architecture_tool`
- ✅ `workflow_tool`
- ✅ `api_tool`
- ✅ `symbol_tool`
- ✅ `quality_tool`
- ✅ `security_tool`

---

## 5. Design Decisions

### 5.1 Why snake_case?

The Tool Registry uses snake_case because:
1. **Python convention**: Python modules and functions typically use snake_case
2. **Consistency**: All existing tool registrations used snake_case
3. **File naming**: Tool files are named `symbol_tool.py`, `architecture_tool.py`, etc.

### 5.2 Why change Query Planner instead of Tool Registry?

1. **Less invasive**: Query Planner is new (Phase 5), Tool Registry is established (Phase 4)
2. **Consistency**: All tool-related code uses snake_case (tool files, registry, definitions)
3. **Simpler**: Single file change vs. updating 6 tool files + registry

### 5.3 Why not support both formats?

1. **Complexity**: Supporting both formats adds unnecessary complexity
2. **Debugging**: Single convention is easier to debug and maintain
3. **Error prevention**: Explicit naming mismatch prevents silent errors

---

## 6. Impact Assessment

### 6.1 Positive Impact

- ✅ Tools are now correctly resolved and executed
- ✅ No more silent fallback to RAG when tools should be used
- ✅ Enhanced logging helps debug future issues
- ✅ Comprehensive runtime integration tests prevent regressions

### 6.2 Breaking Changes

- **None**: This is an internal fix; external API unchanged
- **Documentation**: Updated Phase 5 tests and documentation to reflect snake_case names

### 6.3 Performance Impact

- **Negligible**: String comparison overhead is minimal
- **No new latency**: Fix doesn't add any processing steps

---

## 7. Lessons Learned

### 7.1 Naming Convention Alignment

**Lesson**: Ensure naming conventions are aligned across all layers of the system.

**Prevention**: 
- Define naming conventions in architecture documentation
- Add integration tests that verify naming consistency
- Use code review to catch naming mismatches

### 7.2 Early Integration Testing

**Lesson**: Runtime integration issues should be caught during development, not after deployment.

**Prevention**:
- Add integration tests alongside unit tests
- Test the full execution path (Intent → Planner → Registry → Executor)
- Verify tool registration in CI/CD pipeline

### 7.3 Enhanced Error Logging

**Lesson**: When a tool is not found, log the available tools to aid debugging.

**Prevention**:
- Add context to error messages (available tools, expected names)
- Use structured logging for easier parsing
- Monitor error logs for registration issues

---

## 8. Conclusion

The runtime integration bug was caused by a simple naming convention mismatch between the Query Planner (Phase 5) and the Tool Registry (Phase 4). The fix was straightforward:

1. Updated Query Planner to use snake_case tool names
2. Enhanced error logging to show available tools
3. Updated tests to match the corrected naming
4. Added comprehensive runtime integration tests

The fix ensures that tools are correctly resolved and executed, eliminating silent fallbacks to RAG when specialized tools should be used. All tests pass, and the system now correctly handles the specified queries.

---

**Fix Date**: 2026-08-05  
**Status**: ✅ RESOLVED  
**Tests Passing**: 100/100 copilot and tool-related tests
