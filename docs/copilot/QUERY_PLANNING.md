# QUERY_PLANNING.md

### CodeGraph — Phase 5 Query Planning

_Describes the deterministic reasoning and planning layer that converts classified intents into structured execution plans._

---

## 1. Overview

Phase 5 introduces a **Query Planner** that sits between the Intent Router and the Tool Router. It transforms a classified intent into a structured execution plan that specifies:

- **Required tools**: Which specialized tools should execute
- **Required memory**: Which Repository Memory artifacts to retrieve
- **Retrieval strategy**: Whether and how to run hybrid retrieval
- **Reasoning steps**: Ordered steps for multi-step questions
- **Expected output type**: The structure the LLM should produce

The planner uses **deterministic rules** rather than LLM inference, ensuring predictable performance and low latency.

---

## 2. Architecture

### 2.1 Pipeline Integration

```
User Question
    ↓
Intent Router (Phase 1)
    ↓
Query Planner (Phase 5 NEW)
    ↓
Tool Router (Phase 4)
    ↓
Tool Executor (Phase 4)
    ↓
Context Builder (Phase 4 extended)
    ↓
Prompt Builder → LLM
```

### 2.2 Query Planner Location

**File:** `backend/app/copilot/query_planner.py`

**Class:** `QueryPlanner`

**Key Method:** `plan_query(query, intent, entities, repository_id) -> QueryPlan`

---

## 3. QueryPlan Schema

**File:** `backend/app/copilot/models/query_plan_models.py`

### 3.1 QueryPlan Model

```python
class QueryPlan(BaseModel):
    original_query: str                    # The original user query
    intent: str                            # Classified intent from Intent Router
    required_tools: List[str]              # Tool names to execute (e.g., "ArchitectureTool")
    required_memory: List[str]             # Memory types to retrieve (e.g., "module_memory")
    retrieval_required: bool               # Whether hybrid retrieval should run
    retrieval_strategy: str                # Strategy: symbol_table_lookup, hybrid_semantic, etc.
    reasoning_steps: List[str]             # Ordered reasoning steps for multi-step questions
    expected_output_type: str              # Output structure: direct_match_list, explanation, etc.
    entities: List[Dict[str, str]]        # Extracted entities (name, type)
    confidence: float                      # Planner confidence (0.0–1.0)
    fallback_triggered: bool               # Whether this is a fallback plan
    planning_trace: List[Dict[str, Any]]   # Internal trace of planning decisions
```

### 3.2 QueryStep Model

```python
class QueryStep(BaseModel):
    step_number: int                       # Order of this step
    description: str                       # Human-readable description
    tools: List[str]                       # Tools to execute in this step
    memory: List[str]                      # Memory to retrieve in this step
    retrieval: bool                        # Whether retrieval is needed
    output_dependency: Optional[str]       # If this step depends on previous output
```

---

## 4. Deterministic Planning Rules

### 4.1 Intent → Tool Mapping

| Intent | Base Tools | Multi-Tool Overrides |
|--------|-----------|---------------------|
| `file_lookup` | `SymbolTool` | — |
| `code_explanation` | `SymbolTool` | — |
| `workflow` | `WorkflowTool` | — |
| `architecture` | `ArchitectureTool` | + `WorkflowTool`, `APITool` if "upload" in query |
| `api_flow` | `APITool` | — |
| `quality_analysis` | `QualityTool` | — |
| `security_analysis` | `SecurityTool` | + `SymbolTool` if "vulnerability" in query |
| `bug_analysis` | `SecurityTool`, `SymbolTool` | — |
| `general_query` | [] (none) | — |

### 4.2 Intent → Memory Mapping

| Intent | Base Memory | Keyword Enrichment |
|--------|-------------|-------------------|
| `file_lookup` | `symbol_table` | — |
| `code_explanation` | `symbol_table`, `module_memory` | — |
| `workflow` | `workflow_memory`, `route_memory` | — |
| `architecture` | `architecture_memory`, `module_memory`, `dependency_memory` | — |
| `api_flow` | `api_memory`, `route_memory` | — |
| `quality_analysis` | `module_memory`, `file_memory` | — |
| `security_analysis` | `symbol_table`, `module_memory` | — |
| `bug_analysis` | `symbol_table`, `module_memory` | — |
| `general_query` | `module_memory`, `file_memory` | + `api_memory` if "api" in query, + `configuration_memory` if "config" in query, + `database_schema_memory` if "database" or "schema" in query |

### 4.3 Intent → Retrieval Strategy

| Intent | Strategy | Override Patterns |
|--------|----------|-------------------|
| `file_lookup` | `symbol_table_lookup` | Override to `symbol_table_lookup` if "where is" + symbol keyword |
| `code_explanation` | `hybrid_semantic` | — |
| `workflow` | `graph_traversal` | — |
| `architecture` | `hybrid_semantic` | — |
| `api_flow` | `graph_traversal` | — |
| `quality_analysis` | `hybrid_semantic` | — |
| `security_analysis` | `hybrid_semantic` | — |
| `bug_analysis` | `hybrid_semantic` | — |
| `general_query` | `hybrid_semantic` | — |

### 4.4 Intent → Expected Output Type

| Intent | Output Type |
|--------|-------------|
| `file_lookup` | `direct_match_list` |
| `code_explanation` | `explanation` |
| `workflow` | `trace` |
| `architecture` | `analysis` |
| `api_flow` | `trace` |
| `quality_analysis` | `analysis` |
| `security_analysis` | `analysis` |
| `bug_analysis` | `analysis` |
| `general_query` | `general` |

---

## 5. Multi-Step Question Detection

The planner detects multi-step questions and decomposes them into ordered reasoning steps.

### 5.1 Detection Patterns

| Pattern | Example | Reasoning Steps |
|---------|---------|-----------------|
| "Explain X and identify Y" | "Explain authentication flow and identify vulnerabilities" | 1. Understand and analyze: X<br>2. Identify and locate: Y<br>3. Combine findings |
| "Explain X and find issues" | "Explain upload workflow and find issues" | 1. Understand the component or workflow<br>2. Analyze for issues or vulnerabilities<br>3. Document findings with evidence |
| Security analysis | "Find security issues" | 1. Identify relevant components and symbols<br>2. Analyze code for security issues or bugs<br>3. Trace data flow and dependencies<br>4. Compile findings with evidence |
| Architecture explanation | "Explain architecture" | 1. Identify relevant modules and components<br>2. Analyze architectural structure<br>3. Trace dependencies and relationships<br>4. Document architecture with evidence |
| Workflow tracing | "Trace upload flow" | 1. Identify entry point<br>2. Trace execution path<br>3. Document workflow steps |

### 5.2 Default Single-Step

For queries that don't match multi-step patterns, the planner generates a single step:
- "Execute {intent} analysis"

---

## 6. Confidence Calculation

The planner calculates confidence based on:

1. **Base confidence**: 0.5 (unknown intents start lower)
2. **Tool availability**: +0.3 if tools are available
3. **Known intent**: +0.1 if intent is in the mapping
4. **Keyword match**: +0.1 if query contains intent-specific keywords
5. **Unknown intent penalty**: -0.2 if intent is not recognized

**Range**: 0.0 to 1.0

**Fallback threshold**: If confidence < 0.5, the planner triggers fallback mode.

---

## 7. Fallback Handling

When the planner cannot determine a high-confidence plan, it triggers fallback:

1. **Set `fallback_triggered = True`**
2. **Clear specialized tools**: `required_tools = []`
3. **Use broad memory**: `required_memory = ["module_memory", "file_memory"]`
4. **Enable retrieval**: `retrieval_required = True`, `retrieval_strategy = "hybrid_semantic"`
5. **General output**: `expected_output_type = "general"`
6. **Clear reasoning steps**: `reasoning_steps = []`

**Important**: The fallback never blocks the user. It always provides a safe RAG-based path.

---

## 8. Integration Points

### 8.1 CopilotEngine Integration

**File:** `backend/app/copilot/copilot_engine.py`

The CopilotEngine now:
1. Gets intent from Intent Router
2. Calls `query_planner.plan_query()` to create a QueryPlan
3. Merges the QueryPlan into the execution plan
4. Passes the enriched plan to Tool Executor and Context Builder

```python
# Phase 5: Query planning
query_plan = self.query_planner.plan_query(
    query=query,
    intent=intent,
    entities=intent_plan.get("entities", []),
    repository_id=repository_id,
)

# Merge query plan into execution plan
plan.update({
    "intent": query_plan.intent,
    "required_tools": query_plan.required_tools,
    "required_memory": query_plan.required_memory,
    "retrieval_required": query_plan.retrieval_required,
    "retrieval_strategy": query_plan.retrieval_strategy,
    "reasoning_steps": query_plan.reasoning_steps,
    "expected_output_type": query_plan.expected_output_type,
    "query_plan": query_plan.model_dump(mode="json"),
})
```

### 8.2 ToolExecutor Integration

**File:** `backend/app/copilot/tool_executor.py`

The ToolExecutor now:
1. Extracts `required_tools` from the query plan
2. If `required_tools` is provided, uses those directly
3. Otherwise, falls back to ToolRouter for capability-based resolution

```python
# Phase 5: Use required_tools from query plan if available
required_tools = plan.get("required_tools", [])
specialized = self.execute_specialized_tools(
    repository_id, query, intent, required_tools=required_tools
)
```

### 8.3 ContextBuilder Integration

**File:** `backend/app/copilot/context_builder.py`

The ContextBuilder now:
1. Uses `retrieval_required` from the query plan
2. Uses `required_memory` from the query plan
3. Includes `retrieval_strategy`, `reasoning_steps`, and `expected_output_type` in the context

```python
# Phase 5: Use query plan's retrieval_required and required_memory
retrieval_required = (plan or {}).get("retrieval_required", True)
required_memory = (plan or {}).get("required_memory", [])

# Phase 5: Include query plan metadata in context
return {
    # ... existing fields ...
    "retrieval_strategy": (plan or {}).get("retrieval_strategy", "hybrid_semantic"),
    "required_memory": required_memory,
    "reasoning_steps": (plan or {}).get("reasoning_steps", []),
    "expected_output_type": (plan or {}).get("expected_output_type", "general"),
}
```

### 8.4 ToolRegistry Integration

**File:** `backend/app/copilot/tool_registry.py`

Added `get_tool_definition()` method for query planner to look up tool metadata by name.

```python
def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
    """Alias for get_definition for Phase 5 query planner integration."""
    return self._definitions.get(name)
```

---

## 9. Planning Examples

### 9.1 File Lookup

**Query:** "Where is upload implemented?"

**Plan:**
```json
{
  "intent": "file_lookup",
  "required_tools": ["SymbolTool"],
  "required_memory": ["symbol_table"],
  "retrieval_required": true,
  "retrieval_strategy": "symbol_table_lookup",
  "reasoning_steps": ["Execute file_lookup analysis"],
  "expected_output_type": "direct_match_list",
  "confidence": 0.9
}
```

### 9.2 Workflow Tracing

**Query:** "Explain upload workflow"

**Plan:**
```json
{
  "intent": "workflow",
  "required_tools": ["WorkflowTool"],
  "required_memory": ["workflow_memory", "route_memory"],
  "retrieval_required": true,
  "retrieval_strategy": "graph_traversal",
  "reasoning_steps": [
    "Identify entry point",
    "Trace execution path",
    "Document workflow steps"
  ],
  "expected_output_type": "trace",
  "confidence": 0.9
}
```

### 9.3 Architecture Analysis

**Query:** "Explain upload architecture"

**Plan:**
```json
{
  "intent": "architecture",
  "required_tools": ["ArchitectureTool", "WorkflowTool", "APITool"],
  "required_memory": ["architecture_memory", "module_memory", "dependency_memory"],
  "retrieval_required": true,
  "retrieval_strategy": "hybrid_semantic",
  "reasoning_steps": [
    "Identify relevant modules and components",
    "Analyze architectural structure",
    "Trace dependencies and relationships",
    "Document architecture with evidence"
  ],
  "expected_output_type": "analysis",
  "confidence": 0.9
}
```

### 9.4 Security Analysis

**Query:** "Find authentication vulnerabilities"

**Plan:**
```json
{
  "intent": "security_analysis",
  "required_tools": ["SecurityTool", "SymbolTool"],
  "required_memory": ["symbol_table", "module_memory"],
  "retrieval_required": true,
  "retrieval_strategy": "hybrid_semantic",
  "reasoning_steps": [
    "Identify relevant components and symbols",
    "Analyze code for security issues or bugs",
    "Trace data flow and dependencies",
    "Compile findings with evidence"
  ],
  "expected_output_type": "analysis",
  "confidence": 0.9
}
```

### 9.5 Multi-Step Question

**Query:** "Explain authentication flow and identify vulnerabilities"

**Plan:**
```json
{
  "intent": "security_analysis",
  "required_tools": ["SecurityTool", "SymbolTool"],
  "required_memory": ["symbol_table", "module_memory"],
  "retrieval_required": true,
  "retrieval_strategy": "hybrid_semantic",
  "reasoning_steps": [
    "Understand and analyze: authentication flow",
    "Identify and locate: vulnerabilities",
    "Combine findings into comprehensive answer"
  ],
  "expected_output_type": "analysis",
  "confidence": 0.9
}
```

### 9.6 Fallback

**Query:** "What is the meaning of life?"

**Plan:**
```json
{
  "intent": "general_query",
  "required_tools": [],
  "required_memory": ["module_memory", "file_memory"],
  "retrieval_required": true,
  "retrieval_strategy": "hybrid_semantic",
  "reasoning_steps": ["Execute general_query analysis"],
  "expected_output_type": "general",
  "confidence": 0.7
}
```

---

## 10. Performance Considerations

### 10.1 Planning Latency

The Query Planner is designed to be lightweight:
- **Deterministic rules**: No LLM calls
- **Simple pattern matching**: String contains checks
- **Expected latency**: < 5ms per query

### 10.2 Tool Selection Accuracy

Deterministic rules ensure:
- **Predictable behavior**: Same query always produces same plan
- **High precision**: Tools only selected when clearly needed
- **Recall**: Fallback to RAG ensures no query is blocked

### 10.3 Retrieval Impact

The planner optimizes retrieval:
- **Symbol table lookup** for "where is" questions (faster than semantic search)
- **Graph traversal** for workflow questions (more accurate than semantic search)
- **Hybrid semantic** only when needed (general queries, explanations)

---

## 11. Testing

**File:** `backend/tests/test_phase5_query_planner.py`

### 11.1 Test Coverage

- **Schema tests**: QueryPlan and QueryStep validation
- **Planner tests**: Intent-to-tool, intent-to-memory, retrieval strategy mapping
- **Multi-step tests**: Pattern detection and decomposition
- **Integration tests**: CopilotEngine, ToolExecutor, ContextBuilder integration
- **Specification tests**: All 5 test cases from Phase 5 specification

### 11.2 Test Results

All 23 tests pass:
- 3 schema tests
- 11 planner tests
- 3 integration tests
- 5 specification tests

---

## 12. Design Decisions

### 12.1 Deterministic vs. LLM Planning

**Decision**: Use deterministic rules instead of LLM-based planning.

**Rationale**:
- **Performance**: Deterministic rules are faster (< 5ms vs. 500ms+ for LLM)
- **Predictability**: Same query always produces same plan
- **Debuggability**: Rules are transparent and easy to debug
- **Cost**: No LLM API costs for planning

### 12.2 Tool Selection Strategy

**Decision**: Use intent-based mapping with keyword overrides.

**Rationale**:
- **Simplicity**: Clear mapping from intent to tools
- **Flexibility**: Keyword overrides handle complex queries
- **Maintainability**: Easy to add new intents and tools

### 12.3 Fallback Behavior

**Decision**: Never block the user; always provide safe RAG fallback.

**Rationale**:
- **Reliability**: System always responds, even for unclear queries
- **User experience**: No "I don't understand" failures
- **Safety**: RAG provides reasonable answers for most queries

### 12.4 Reasoning Steps Storage

**Decision**: Store reasoning steps in the plan but don't expose chain-of-thought to users.

**Rationale**:
- **Internal use**: Steps guide the pipeline but aren't shown to users
- **Transparency**: Steps are logged for debugging
- **Privacy**: No intermediate reasoning exposed to end users

---

## 13. Future Enhancements

### 13.1 Entity Extraction

Currently, entities are passed from Intent Router but not deeply used. Future work:
- Extract named entities (functions, classes, files) from queries
- Use entities to improve tool and memory selection
- Support entity-based retrieval strategies

### 13.2 Dynamic Tool Discovery

Currently, tools are statically mapped. Future work:
- Discover available tools at runtime
- Match tools to queries based on descriptions
- Support plugin-based tool registration

### 13.3 Learning from Feedback

Currently, rules are static. Future work:
- Track plan execution success/failure
- Adjust confidence thresholds based on feedback
- Learn new patterns from successful queries

---

## 14. References

- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Data Flow](../architecture/DATA_FLOW.md)
- [RAG Pipeline](../architecture/RAG_PIPELINE.md)
- [Tool Routing](TOOL_ROUTING.md)
- [Context Assembly](CONTEXT_ASSEMBLY.md)
- [Implementation Checklist](../implementation/IMPLEMENTATION_CHECKLIST.md)
