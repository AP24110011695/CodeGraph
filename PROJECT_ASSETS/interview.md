# Interview notes

## Talking points

- Problem: large repos don’t come with a durable architectural view; search alone isn’t enough.
- Approach: separate engines per concern; orchestrate via planning + thin APIs.
- Copilot is wiring, not another analyzer.
- Impact reuses graph traversal rather than a second BFS implementation.
- RC-1 is honest about stubs (auth, Redis, live git).

## STAR — registration gap

- **S:** 18 API tests failing on quality/smells/refactoring.
- **T:** Green the suite without rewriting analyzers.
- **A:** Found routers never registered in `main.py`; wired them; shared path helper for upload roots.
- **R:** Full suite green; endpoints reachable.

## STAR — impact analysis

- **S:** Needed “what breaks if I change X?”
- **T:** Ship impact without forking graph code.
- **A:** Composed ImpactEngine on GraphQuery/traverser + memory/timeline signals.
- **R:** Same path used by agents, reports, and Copilot tools.

## Likely questions

**Is this just an LLM wrapper?**  
No. Graphs, memory, planning, and impact are real modules; the model (or local fallback) synthesizes answers.

**How do you keep modules from sprawling?**  
One package per capability, facade engines, planning for orchestration, rules against duplicated traversal/indexing.

**What’s missing for production?**  
Auth, durable stores, Redis, real VCS providers — listed in `archive/TECH_DEBT.md`.
