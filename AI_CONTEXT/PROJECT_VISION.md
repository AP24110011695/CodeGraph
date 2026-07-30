# Project Vision — CodeGraph

> **Related:** [AI_RULES.md](./AI_RULES.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [ROADMAP.md](./ROADMAP.md)

---

## What CodeGraph is

**CodeGraph is not simply a code search tool.**

It is an **Enterprise AI Software Architecture Platform** that turns repositories into structured, queryable, evolvable architectural knowledge — usable by humans, copilots, planners, and multi-agent systems.

Tagline (from product sources): *The AI Software Architect for Every Codebase.*

---

## Mission

Make every codebase **intelligible, governable, and actionable** through:

- Structural understanding (graphs, architecture, APIs, services)
- Quality and risk intelligence
- Persistent repository memory
- Semantic and RAG-backed context
- Planning and multi-agent execution
- Temporal evolution (timeline) and predictive change impact

---

## Long-term goals

1. **Architecture-first intelligence** — Prefer explanations of structure, coupling, drift, and risk over raw file dumps.
2. **Composable knowledge sources** — Memory, Graph, Semantic, Timeline, Impact, RAG as interchangeable context providers.
3. **Agentic engineering workflows** — Planning Engine selects modules; agents execute specialized roles.
4. **Enterprise integrations** — GitHub, Jira, CI/CD, notifications, workspaces (many clients are currently mock/stubbed; contracts exist).
5. **Incremental truth** — Snapshot + incremental indexing so knowledge stays current without full re-index.
6. **Observability & reliability** — Telemetry, workers, workflows, reliability controls as first-class platform layers.

---

## Engineering philosophy

- **Reuse over rewrite** — New CG modules compose existing engines.
- **Abstractions at boundaries** — Providers for history, cache backends, VCS/diff inputs.
- **Thin edges, rich cores** — FastAPI routers stay thin; engines own domain logic.
- **Evidence over invention** — Document and implement only what the repository supports.
- **Self-documenting system** — `AI_CONTEXT/` keeps future AI sessions aligned with reality.

---

## Design philosophy

```text
Upload / Sync
    → Scan / Parse / Index
    → Graphs + Metrics + Quality + Security + Risk
    → Memory + Semantic + RAG
    → Reasoning + Planning + Agents
    → Timeline + Impact (+ future Copilot depth)
```

Each layer **enriches** the previous; it must not replace or fork it.

---

## Future direction (directional, not invented modules)

Based on existing stubs and debt (see [TECH_DEBT.md](./TECH_DEBT.md)):

- Real Git / GitHub / GitLab / Bitbucket history providers
- Real LLM backends for chat/explain (today partially mocked)
- Redis-backed distributed cache
- Production vector database
- Event streaming beyond in-process bus
- Register missing quality/smells/refactoring routers
- Deeper PR/diff-driven impact analysis (extension points already exist)

Everything newly built should move toward this vision without inventing parallel platforms.
