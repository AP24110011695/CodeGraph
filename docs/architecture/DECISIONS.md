# DECISIONS.md

### CodeGraph — Architectural Decisions

---

## 1. Overview
This document records major architectural decisions, trade-offs, and rationale for the CodeGraph system.

## 2. Active Decisions

### Decision 1: Structured Intent Routing over Open-Ended Prompting
- **Context**: CodeGraph originally suffered from generic, undifferentiated prompting which caused LLM hallucinations and repetitive "Analysis Results" headers.
- **Decision**: Introduce an Intent Router and Query Planner to classify every query and select an explicit pipeline (RAG-only, RAG+tools, graph traversal, etc.).
- **Rationale**: The system should never ask the LLM an open-ended question. Narrowing the LLM's job to filling an evidence-bound template increases precision and correctness.
- **Reference**: [Copilot Rebuild Plan](COPILOT_REBUILD_PLAN.md)

### Decision 2: Separated Repository Memory Stores
- **Context**: A single flattened "architecture summary" was previously injected into every prompt.
- **Decision**: Treat Repository Memory as 11 independently queryable structured stores (e.g., Symbol Table, Dependency Memory). Prefer deterministic tools over LLM inference wherever a deterministic answer exists.
- **Rationale**: Removes hallucination risk at the memory layer and allows cheap incremental recomputation on file change.
- **Reference**: [System Architecture](SYSTEM_ARCHITECTURE.md)

### Decision 3: Closed-Loop Answer Verification
- **Context**: Raw pass-through of LLM output with no validation.
- **Decision**: Implement Answer Verification that checks intent match, citations, and evidence coverage.
- **Rationale**: Triggers bounded retry with corrective instructions if the model hallucinates or fails to cite sources.
- **Reference**: [System Architecture](SYSTEM_ARCHITECTURE.md)

## 3. Pending Decisions
TODO: Document future architectural decisions here.

### Decision 4: Explicit Unavailable States (Phase 0 Stabilization)
- **Context**: The system previously fell back to mock scores (e.g., `0`, `78`) or demo paragraphs when analysis data was missing or not yet indexed, which eroded trust and led to misleading UI/Copilot outputs.
- **Decision**: Remove all hardcoded mock fallback values across the application. When a metric or analysis is missing, components must explicitly return an "unavailable" state (e.g., `{"status": "unavailable", "value": null, "reason": "..."}`) rather than a misleading zero or default number.
- **Rationale**: A value of `0` implies that an analysis ran and scored `0`. An explicit `null`/unavailable state ensures the UI and Copilot only present data that actually exists, correctly representing partial index states.

### Decision 5: Intent-Aware Prompt Templates & Structured Context Assembly (Phase 1)
- **Context**: The Copilot previously used a single monolithic system prompt for all query types, leading to generic "Analysis Results / Key Findings / Recommendations" headers regardless of what was asked. Retrieved RAG chunks were concatenated as an unstructured blob.
- **Decision**: Introduce six deterministic Phase 1 intents (`file_lookup`, `code_explanation`, `workflow`, `architecture`, `bug_analysis`, `general_query`). Each intent maps to a distinct output format template in the Prompt Builder. Retrieved context items are formatted as structured `FILE / SYMBOL / REASON / CODE` blocks before injection.
- **Rationale**: Intent-specific templates enforce answer format discipline at the system-prompt level, eliminating generic headers without requiring LLM post-processing. Structured context attribution allows the model to cite sources rather than generating unsupported claims.
- **Reference**: [COPILOT_REBUILD_PLAN.md §4](COPILOT_REBUILD_PLAN.md), [PROMPT_PIPELINE.md](PROMPT_PIPELINE.md)
- [System Architecture](SYSTEM_ARCHITECTURE.md)
