# README_AI — Start Here

**CodeGraph** is an **Enterprise AI Software Architecture Platform** — *The AI Software Architect for Every Codebase.*

**Release:** `1.0.0-rc.1` (Release Candidate 1 — green suite).

It is **not** merely a code search tool. See [PROJECT_VISION.md](./PROJECT_VISION.md).

Portfolio / resume assets: [`../PROJECT_ASSETS/`](../PROJECT_ASSETS/).

---

## Where to start

1. Read this file.  
2. Follow [PROMPT_GUIDELINES.md](./PROMPT_GUIDELINES.md).  
3. Load the authoritative docs below.  
4. Inspect `backend/app/` — especially `main.py` and the target domain package.  
5. Implement **only** the requested CG module (or polish task). Prefer composition.

---

## Authoritative AI_CONTEXT documents

| Document | Role |
|----------|------|
| [AI_RULES.md](./AI_RULES.md) | Permanent engineering rules |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Implemented architecture |
| [MODULE_INDEX.md](./MODULE_INDEX.md) | Subsystem index |
| [ROADMAP.md](./ROADMAP.md) | Phases & completion |
| [CURRENT_STATUS.md](./CURRENT_STATUS.md) | Live status |
| [TECH_DEBT.md](./TECH_DEBT.md) | Known issues & stubs |
| [LESSONS_LEARNED.md](./LESSONS_LEARNED.md) | Engineering history |
| [CHANGELOG_AI.md](./CHANGELOG_AI.md) | Per-CG changelog |
| [CODING_STANDARDS.md](./CODING_STANDARDS.md) | Repo conventions |
| [PROJECT_VISION.md](./PROJECT_VISION.md) | Long-term vision |
| [PROMPT_GUIDELINES.md](./PROMPT_GUIDELINES.md) | Mandatory workflow |

---

## How to navigate the project

| Path | Purpose |
|------|---------|
| `backend/app/main.py` | App + router registration |
| `backend/app/<domain>/` | Business engines |
| `backend/app/api/` | Thin HTTP layer |
| `backend/app/schemas/` | Pydantic contracts |
| `backend/tests/` | pytest suite |
| `docs/` | Human architecture/API overviews |
| `PROJECT_ASSETS/` | Portfolio & interview pack |
| `frontend/` | UI scaffold (backend is RC-1 focus) |

---

## Standard workflow (short)

Read AI_CONTEXT → Inspect code → Reuse engines → Implement one change → Test → Validate APIs → Update living docs → Return summary.

---

## Implementation checklist

- [ ] Read rules, architecture, status, debt, lessons  
- [ ] Locate reusable engines  
- [ ] Add package / schemas / API / tests as needed  
- [ ] Register router in `main.py`  
- [ ] Wire Planning/Agents/Cache/Telemetry only if required  
- [ ] No duplicated indexing / traversal / memory / business logic  

## Validation checklist

- [ ] `pytest tests/ -q` from `backend/`  
- [ ] Uvicorn + affected endpoints + `/health`  
- [ ] No new regressions  
- [ ] Debt updated if limitations remain  

## Documentation update checklist

- [ ] CURRENT_STATUS.md  
- [ ] ROADMAP.md  
- [ ] LESSONS_LEARNED.md  
- [ ] CHANGELOG_AI.md  
- [ ] MODULE_INDEX.md  
- [ ] TECH_DEBT.md (if needed)  
- [ ] Root CHANGELOG.md for user-facing releases  
