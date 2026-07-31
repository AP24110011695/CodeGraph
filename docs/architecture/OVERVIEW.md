# Architecture

Short overview of the backend. Full notes: `AI_CONTEXT/ARCHITECTURE.md`.

```text
HTTP (app/api) → engines (app/<domain>) → cache / telemetry / workers
```

Copilot flow:

```text
POST /copilot/chat
  → plan(query)
  → run tools (memory, RAG, timeline, impact, agents, …)
  → synthesize answer
```

Design habits we stuck to:

- Don’t reimplement indexing or graph traversal in new features
- Keep routers thin
- Swap cache / LLM / history behind interfaces where possible
