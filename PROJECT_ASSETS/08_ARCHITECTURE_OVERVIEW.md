# Architecture Overview (Interview / Portfolio)

## Layers

1. **HTTP** — `app/api/*` thin routers  
2. **Contracts** — `app/schemas/*`  
3. **Domain engines** — `app/<capability>/*` facades  
4. **Platform** — cache, telemetry, workflows, workers, reliability  

## Key runtime path

User question → Copilot → Planning (intent + module order) → ToolExecutor calls Memory/RAG/Timeline/Impact/Reports/Agents → LLM/local synthesis → structured response (confidence, citations, follow-ups).

## Non-negotiables

- Never duplicate indexing, retrieval, graph BFS, or domain scoring  
- Agents call engines; agents do not call other agents directly  
- Optional enrichment must not fail primary operations  

See also: `docs/architecture/OVERVIEW.md`, `AI_CONTEXT/ARCHITECTURE.md`.
