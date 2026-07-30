# Lessons Learned — CodeGraph Engineering History

> **Append after every completed CG module.** Do not rewrite history; add a new section.  
> **Related:** [CHANGELOG_AI.md](./CHANGELOG_AI.md) · [AI_RULES.md](./AI_RULES.md)

---

## CG-070 — Unified Intelligence Orchestrator / CodeGraph Copilot (2026-07-31)

### Problem solved

Users need a single AI Software Architect interface that answers engineering questions by coordinating every intelligence subsystem — without a second copy of planning, retrieval, reasoning, or analysis.

### Design decisions

- Copilot is an **orchestration facade** only: Planning decides intent/modules; `ToolExecutor` invokes existing engines; Agents run when execute/use_agents requests them.  
- Conversation Memory is **independent** of Repository Memory (follow-ups vs durable repo summaries).  
- `ProviderManager` wraps `LLMProvider` ABC (+ local heuristic fallback); no vendor logic inside `CopilotEngine`.  
- Structured engineering responses (answer, confidence, tools, citations, recommendations, follow-ups).  
- Legacy `POST /copilot/{upload_id}` capability-routing path retained for compatibility.

### Trade-offs

- Default `chat` runs tools from the plan without always engaging multi-agent collaboration (faster); `execute` opts into agents.  
- Local heuristic provider used when cloud keys are absent — deterministic demos, not production LLM quality.  
- Knowledge Graph tool surfaces memory-backed structure rather than rebuilding graphs.

### Architecture decisions

- Package modules: conversation_manager/memory, context_builder, prompt_builder, tool_executor, provider_manager, response_builder, post_processor, execution_statistics, copilot_engine.  
- APIs: `POST /chat`, `POST /execute`, `GET|DELETE /history` registered before legacy `/{upload_id}`.  
- New tools register via `ToolExecutor.register` without modifying the engine.

### Lessons learned

- Static routes (`/chat`, `/history`) must precede path params.  
- Parameter names that match imported singletons (`response_builder`) shadow imports — alias imports in the facade.  
- Optional enrichment/tools must never fail the primary orchestration path.

### Future considerations

- Wire OpenAI/Claude/Gemini/Groq/Ollama/Azure for synthesis.  
- Register Performance/Testing/Cloud/DevOps/Database/Code-Review agents as tools.  
- Persist conversation memory beyond process lifetime.

### Why this solution

Matches AI_RULES: composition over duplication, Planning for orchestration, thin API, DI-friendly providers/tools.

---

## CG-069 — Engineering Intelligence Report Generator (2026-07-31)

### Problem solved

Stakeholders need a single composed engineering report spanning health, architecture, memory, timeline, impact, debt, risk, and recommendations — without re-running every analyzer.

### Design decisions

- New `ReportEngine` facade that **collects** from Memory, Architecture Reasoning, Timeline, and Impact.  
- `SectionComposer` + `HealthScorer` produce typed report sections and composite health.  
- `ReportExporter` ABC with JSON/Markdown implemented; HTML/PDF stubs for future.  
- Distinct from existing `architecture_report` (path-based scan/markdown) — CG-069 is intelligence-composition over `repository_id`.

### Trade-offs

- Security/quality content comes from memory notes and composed signals, not a fresh security scan (avoids duplication/heavy I/O).  
- GET `/reports/{id}` auto-generates an executive report if none exist — convenient, slightly write-on-read.

### Architecture decisions

- Package `app/engineering_reports/` + `/reports` API.  
- Does not replace `/architecture-report`.  
- Cache keys for report + summary.

### Lessons learned

- Keep exporters behind an interface so PDF/HTML never touch business logic.  
- Register `/summary` route before ambiguous patterns; FastAPI path specificity handled by declaring summary route explicitly.  
- Composition beats a second architecture report engine.

### Future considerations

- HTML/PDF exporters; persist `ReportStore` beyond process memory.  
- Optional section from real security/quality engines when index READY.

### Why this solution

Matches AI_RULES: reuse, no duplicate analysis, thin API, DI-friendly exporters.

### Problem solved

Need to predict blast radius, API contract risk, architecture coupling, and propagation paths **before** a change lands — without re-indexing or forking graph algorithms. Also surface affected modules, services, APIs, symbols, and repository-memory refresh hints.

### Design decisions

- Facade `ImpactEngine` composing specialized analyzers including `MemoryImpact`.  
- Reuse `RelationshipTraverser` + `GraphQuery` for propagation; reuse Semantic `SymbolResolver` for symbols.  
- Seed lightweight `KnowledgeGraph` from Repository Memory + Timeline co-evolution when no external graph injected.  
- `related_files` / `change_type` as future Git diff / PR / CI seam.  
- Risk analyzer **composes** signals; does not call full `RiskEngine` pipeline.  
- Non-destructive `[Impact]` memory notes for refresh awareness.

### Trade-offs

- Lightweight graphs are approximate vs full indexed KG — confidence score reflects memory/timeline/semantic/external-graph usage.  
- Summary endpoint may run a few analyses to bootstrap — cache mitigates repeats.  
- Q&A intent order matters (`propagation` before `service`) to avoid false matches.

### Architecture decisions

- Package `app/impact_analysis/` following Timeline-style module layout.  
- Planning intent `impact_analysis` routes to Impact Analysis Engine.  
- `ImpactAgent` registered; DependencyAgent optionally composes Impact answers.

### Lessons learned

- Extension points (`graph_provider`, `related_files`) prevent later rewrites.  
- Explicit top-level `affected_*` fields improve API usability for agents/copilot.  
- Register cache key helpers on `CacheKeys` with the feature.

### Future considerations

- Wire real KG from index when `repository_id` has READY index.  
- PR review / CI should call Impact with changed file lists.

### Why this solution

Matches AI_RULES: composition, no duplicate traversal/indexing/retrieval, thin API, DI-friendly providers.

---

## CG-067 — Repository Timeline Intelligence (2026-07-31)

### Problem solved

Repositories were analyzed as snapshots only; product needed evolution, hotspots, ownership, and historical narratives as a first-class knowledge source.

### Design decisions

- `HistoryProvider` ABC with `LocalMetadataHistoryProvider` default.  
- Stub forge/git providers for future swap without engine changes.  
- Timeline-scoped `architecture_drift` distinct from `app/architecture_drift` snapshot engine.  
- Enrich Memory with `[Timeline]` notes non-destructively.

### Trade-offs

- Synthetic deterministic commits when no VCS — enables tests/demos but is not true git history.  
- Must document clearly so assistants do not treat synthetic history as VCS truth.

### Architecture decisions

- Integrate Planning (`timeline_analysis`), TimelineAgent, RAG context selector, Copilot capability keywords.  
- Specific routes (`/evolution`, `/hotspots`) registered before `/{repository_id}`.

### Lessons learned

- Route ordering in FastAPI matters for static path segments.  
- Optional enrichment must never fail the primary response.  
- Pre-existing test failures (quality/smells/refactoring) are registration debt — document, don’t “fix” by skipping.

### Future considerations

- Implement real GitHistoryProvider.  
- Persist timeline artifacts beyond cache.

### Why this solution

Provider pattern + reuse of Memory/Snapshots matches enterprise extensibility goals without duplicating indexing.

---

## Foundation (CG-001 … CG-066) — Operating notes

### Observed patterns that worked

- Engine facade + singleton export.  
- Schemas package separation.  
- Thin routers.  
- CacheInterface / TelemetryManager as cross-cutting facades.  
- Planning → Agents for orchestration.

### Recurring risks

- API files can drift from `main.py` registration.  
- Mock clients must stay labeled so they are not mistaken for production.  
- Multiple “architecture” concerns (builder, drift, reasoning, timeline drift) need clear naming in docs and imports.
