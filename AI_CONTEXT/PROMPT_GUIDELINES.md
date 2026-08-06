# Prompt Guidelines — Mandatory AI Workflow

> Every AI assistant (Cursor, Codex, Claude Code, Windsurf, Zed, Devin, OpenHands, …) must follow this workflow for CodeGraph work.

**Entry point:** [README_AI.md](./README_AI.md)

---

## 1. Read first (before any code change)

1. [README_AI.md](./README_AI.md)  
2. [AI_RULES.md](./AI_RULES.md)  
3. [ARCHITECTURE.md](./ARCHITECTURE.md)  
4. [ROADMAP.md](./ROADMAP.md)  
5. [CURRENT_STATUS.md](../archive/CURRENT_STATUS.md)  
6. [TECH_DEBT.md](../archive/TECH_DEBT.md)  
7. [LESSONS_LEARNED.md](../archive/LESSONS_LEARNED.md)  
8. [CHANGELOG_AI.md](./CHANGELOG_AI.md)  
9. [MODULE_INDEX.md](./MODULE_INDEX.md)  
10. [CODING_STANDARDS.md](./CODING_STANDARDS.md) (when implementing)  
11. [PROJECT_VISION.md](./PROJECT_VISION.md) (when making product-direction choices)

---

## 2. Inspect the codebase

- Search `backend/app/` for existing engines solving the same problem.  
- Read `app/main.py` router list before adding APIs.  
- Confirm whether quality/smells/refactoring-style registration gaps apply.  
- **Do not invent** architecture or completed features.

---

## 3. Understand current architecture

- Identify facades to compose.  
- Identify schemas/API patterns to copy.  
- Identify cache/telemetry/planning/agent touchpoints.

---

## 4. Reuse existing systems

Composition over new frameworks. Prefer Memory, GraphQuery, RelationshipTraverser, Planning, Cache, Telemetry, Timeline, Impact, RAG, etc.

---

## 5. Never duplicate logic

Forbidden: second indexers, second BFS, second memory stores, parallel planning stacks.

---

## 6. Implement ONLY the requested CG module

- No drive-by refactors.  
- No fixing unrelated debt unless required for the module or explicitly requested.  
- Document pre-existing failures instead of expanding scope.

---

## 7. Run the complete test suite

```bash
cd backend
python -m pytest tests/ -v
```

---

## 8. Validate APIs

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Exercise new endpoints; confirm `/health`.

---

## 9. Verify no regressions

- Neighboring tests (planning, agents, memory, cache, timeline/impact as relevant) must stay green.  
- If full suite still has the known 18 failures, confirm they are unchanged and noted in TECH_DEBT.

---

## 10. Update living documentation

Always:

- [CURRENT_STATUS.md](../archive/CURRENT_STATUS.md)  
- [ROADMAP.md](./ROADMAP.md)  
- [LESSONS_LEARNED.md](../archive/LESSONS_LEARNED.md)  
- [CHANGELOG_AI.md](./CHANGELOG_AI.md)  
- [MODULE_INDEX.md](./MODULE_INDEX.md)  

If debt changed:

- [TECH_DEBT.md](../archive/TECH_DEBT.md)

---

## 11. Return implementation summary

1. Files created  
2. Files modified  
3. Architecture summary  
4. Test summary  
5. Validation summary  
6. Design decisions  
7. Self review  

---

## Anti-patterns

- Rewriting stable engines “cleanly”  
- Adding Redis/Kafka/LLM “for real” inside an unrelated CG ticket  
- Skipping `main.py` registration  
- Treating root README folder tree as literal  
- Claiming CG-069+ features that are not assigned
