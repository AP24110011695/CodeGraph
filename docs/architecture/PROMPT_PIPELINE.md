# PROMPT_PIPELINE.md

### CodeGraph — Prompt Pipeline Architecture

_Derived from COPILOT_REBUILD_PLAN.md._

---

## 1. Overview
The Prompt Builder constructs the LLM prompt from the execution plan context + instructions. It relies on a set of structural rules that apply to every template. Every query, before it reaches the LLM, is transformed into a fully specified task with an attributed evidence set and an output contract the model is instructed to fill.

## 2. Structural Rules
- **Context injection format**: Every chunk is injected with file path, function/class, module, lines, and reason selected.
- **Citation rule**: Every factual claim must reference a chunk by file path and line range. If information is missing, the model must explicitly state so.
- **Forbidden generic wording**: Banned headers include "Analysis Results", "Key Findings", "Repository Context", "Recommendations" unless genuinely open-ended. Hedge phrases like "typically", "in general" are banned.

## 3. Per-Intent Templates
- **Architecture**: Describe actual structure using module summaries and dependency map.
- **Workflow Tracing**: Trace request flowing through layers in execution order.
- **Security Review**: Evaluate only provided code and analyzer findings.
- **Bug Finding**: Confirm/reject findings from static-analysis.
- **Code Explanation**: Explain specific code using only provided chunks.
- **Refactoring Suggestions**: Base on actual code and complexity/smell-detector output.
- **API Tracing**: Trace API call from invocation through wrapper to definition.
- **Dependency Tracing**: Describe module dependencies using dependency graph edges.
- **File Lookup**: State exact file/lines where requested symbol/pattern occurs.
- **Database Query**: Describe DB interactions using schema memory and actual query/ORM code.
- **Configuration**: Explain config using actual config files and env vars.
- **Performance Analysis**: Identify patterns using code and complexity analyzer output.
- **Testing**: Describe test coverage/structure using actual test files.

## 4. Verification Loop
Answer Verification checks for intent match, citation presence, evidence coverage, and hallucinated citations. On failure, triggers a bounded retry (cap 1) with a corrective addendum.

## 5. References
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Copilot Rebuild Plan](COPILOT_REBUILD_PLAN.md)
