# Architecture Overview

CodeGraph is a layered FastAPI intelligence platform. Engines compose; APIs stay thin.

```mermaid
flowchart TB
  subgraph clients [Clients]
    UI[Frontend / API clients]
    CopilotUI[Copilot chat]
  end
  subgraph api [HTTP Layer]
    FastAPI[FastAPI routers app/api]
  end
  subgraph intelligence [Intelligence Engines]
    Memory[Repository Memory]
    Semantic[Semantic Engine]
    RAG[Advanced RAG]
    Reasoning[Architecture Reasoning]
    Planning[Planning Engine]
    Agents[Multi-Agent Framework]
    Timeline[Timeline Intelligence]
    Impact[Impact Analysis]
    Reports[Engineering Reports]
    Copilot[Copilot Orchestrator]
  end
  subgraph structure [Structure]
    Scan[Scanner / Parser]
    KG[Knowledge Graph]
    Dep[Dependency Graph]
    Index[Indexing / Snapshots]
  end
  subgraph platform [Platform]
    Cache[CacheInterface]
    Telemetry[Telemetry]
    Workflows[Workflows / Workers]
  end
  UI --> FastAPI
  CopilotUI --> FastAPI
  FastAPI --> Copilot
  Copilot --> Planning
  Copilot --> Agents
  Copilot --> Memory
  Copilot --> RAG
  Copilot --> Timeline
  Copilot --> Impact
  Copilot --> Reports
  Agents --> Reasoning
  Agents --> Impact
  Agents --> Timeline
  RAG --> Memory
  RAG --> Semantic
  Impact --> KG
  Timeline --> Memory
  Reports --> Memory
  Reports --> Timeline
  Reports --> Impact
  Scan --> Index
  Index --> KG
  Dep --> KG
  Memory --> Cache
  Timeline --> Cache
  Impact --> Cache
  FastAPI --> Telemetry
  Workflows --> Telemetry
```

## Request flow (Copilot)

```text
POST /copilot/chat
  → PlanningEngine.plan
  → ContextBuilder (Memory + RAG + conversation)
  → ToolExecutor (existing engines)
  → ProviderManager (LLM / local heuristic)
  → structured engineering response
```

## Design principles

1. **Composition over duplication** — never reimplement indexing, traversal, retrieval, or domain scoring.
2. **Thin controllers** — routers validate, call engines, map errors.
3. **Provider seams** — cache, history, LLM providers swap without rewriting facades.
4. **Planning owns orchestration** — multi-agent and Copilot tools follow planning intents.

Authoritative detail: [`AI_CONTEXT/ARCHITECTURE.md`](../AI_CONTEXT/ARCHITECTURE.md).
