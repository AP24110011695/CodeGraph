# TOOL_ROUTING.md

## CodeGraph — Phase 4 Tool Routing

_Describes the Tool Registry, Tool Router, Execution Flow, and Multi-Tool Orchestration introduced in Phase 4._

---

## 1. Overview

Phase 4 introduces deterministic Tool Calling. Instead of routing every query through RAG alone, CodeGraph now selects and executes specialized analysis tools when the intent clearly requires one.

The pipeline is:

```
User Query
     ↓
Intent Router (Phase 1 — unchanged)
     ↓
Tool Router (Phase 4 NEW)
     ↓
Tool Registry (Phase 4 NEW)
     ↓
Tool Executor (Phase 1 — extended, not replaced)
     ↓
Tools (Phase 4 NEW)
     ↓
Context Builder (Phase 4 — extended)
     ↓
Prompt Builder  (Phase 4 — extended)
     ↓
LLM
```

---

## 2. Capability Layer

Tool Calling uses an intermediate Capability layer between Intent and Tool. This allows multiple tools to be selected for a single intent.

```
Intent
  ↓
Capabilities  (e.g., "architecture", "workflow", "api")
  ↓
Tool(s)
```

Example:

| Intent | Capabilities | Tools Invoked |
|--------|-------------|---------------|
| `architecture` | `architecture` | Architecture Tool |
| `workflow` | `workflow` | Workflow Tool |
| `api_flow` | `api` | API Tool |
| `file_lookup` | `symbol` | Symbol Tool |
| `quality_analysis` | `quality` | Quality Tool |
| `security_analysis` | `security` | Security Tool |
| `architecture` + "upload" keyword | `architecture`, `workflow`, `api` | Architecture + Workflow + API Tools |
| `general_query` | (none) | Fallback to RAG |

---

## 3. Tool Registry

**File:** `backend/app/copilot/tool_registry.py`

The `ToolRegistry` class is a central store for all registered tools.

Each tool is registered with:
- A `ToolDefinition` (name, description, capabilities list)
- A `ToolHandler` callable: `(repository_id, query, context) -> ToolResult`

```python
tool_registry.register_tool(definition, handler)
tool_registry.find_tools_by_capabilities(["architecture", "workflow"])
```

Tools self-register on module import from `backend/app/copilot/tools/__init__.py`.

---

## 4. Tool Router

**File:** `backend/app/copilot/tool_router.py`

The `ToolRouter` resolves capabilities from the intent classification, then queries the `ToolRegistry`.

```python
tool_defs = tool_router.resolve_tools(intent, query)
```

Multi-tool detection is done by keyword overrides on top of the base intent map:
- `"upload" in query` → adds `workflow` + `api` capabilities on top of `architecture`
- `"architecture" AND "workflow" in query` → adds both capabilities

**Fallback:** If no capabilities are identified, `resolve_tools()` returns `[]`. The `ToolExecutor` detects an empty list and falls back to the existing RAG-based module pipeline.

---

## 5. Tool Executor (Extended)

**File:** `backend/app/copilot/tool_executor.py`

The `ToolExecutor.execute_plan()` method now:
1. Calls `execute_specialized_tools()` first (Phase 4 path).
2. If tools are found, returns their results immediately.
3. If no tools match the intent, falls back to the original module-based pipeline (RAG Engine, Architecture Analyzer, etc.).

```python
specialized = executor.execute_specialized_tools(repository_id, query, intent)
if specialized:
    return specialized
# else: fall through to RAG module execution
```

---

## 6. Standardized Tool Output Schema

**File:** `backend/app/copilot/models/tool_models.py`

Every tool **must** return a `ToolResult` Pydantic model:

```python
class ToolResult(BaseModel):
    tool: str           # Tool identifier
    summary: str        # Human-readable findings summary
    evidence: List[Dict]  # Structured findings/data
    related_files: List[str]  # Relevant file paths
    confidence: float   # 0.0 – 1.0 confidence score
    metadata: Dict      # Additional tool-specific metadata
```

Confidence is validated at 0.0–1.0. Tools that encounter errors or missing repos return `confidence=0.0`.

---

## 7. Tools Implemented

| Tool | File | Capabilities | Underlying Analyzer |
|------|------|-------------|---------------------|
| Architecture Tool | `tools/architecture_tool.py` | `architecture` | `ArchitectureBuilder`, `DependencyGraph` |
| Workflow Tool | `tools/workflow_tool.py` | `workflow` | `WorkflowMemory` (Repository Memory) |
| API Tool | `tools/api_tool.py` | `api` | `APIMemory` (Repository Memory) |
| Symbol Tool | `tools/symbol_tool.py` | `symbol` | `SymbolTable` (Repository Memory) |
| Quality Tool | `tools/quality_tool.py` | `quality` | `QualityAnalyzer` |
| Security Tool | `tools/security_tool.py` | `security` | `SecurityAnalyzer` |

---

## 8. Context Builder Integration

**File:** `backend/app/copilot/context_builder.py`

`ContextBuilder.build()` now accepts an optional `tool_results` parameter:

```python
context = context_builder.build(
    repository_id, query, tool_results=tool_results
)
```

Tool results are **transformed into structured text evidence** (not raw JSON) before merging into the context. Only `status="ok"` results are included. Failed tool runs are silently excluded.

Output context includes `"tool_results"` key with formatted evidence entries.

---

## 9. Prompt Builder Integration

**File:** `backend/app/copilot/prompt_builder.py`

The `PromptBuilder.build()` renders Phase 4 tool results as clearly labelled blocks:

```
[TOOL ANALYSIS: SECURITY TOOL]
Summary: Found 3 security issues.
Evidence:
  file: src/auth.py
  issue: SQL injection risk in query builder
Related Files: src/auth.py
Confidence: 90%
```

The LLM is instructed to **explain** these findings, not regenerate them.

---

## 10. Fallback

When no specialized tool applies (e.g., `general_query`, `bug_analysis`, `documentation`):
- `tool_router.resolve_tools()` returns `[]`
- `execute_specialized_tools()` returns `[]`
- `execute_plan()` falls through to the existing RAG Engine / module-based pipeline
- No change in behavior for existing intents

---

_End of TOOL_ROUTING.md_
