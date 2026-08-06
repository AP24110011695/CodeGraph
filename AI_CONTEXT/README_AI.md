# AI_CONTEXT

Working notes for people (and coding agents) changing the backend.  
The public entry point for the repo is still the root [README](../README.md).

## Read order

1. [AI_RULES.md](./AI_RULES.md) — engineering constraints  
2. [ARCHITECTURE.md](./ARCHITECTURE.md) — what is actually built  
3. [MODULE_INDEX.md](./MODULE_INDEX.md) — package map  
4. [CURRENT_STATUS.md](../archive/CURRENT_STATUS.md) / [TECH_DEBT.md](../archive/TECH_DEBT.md)  

Also useful: [CODING_STANDARDS.md](./CODING_STANDARDS.md), [ROADMAP.md](./ROADMAP.md), [LESSONS_LEARNED.md](../archive/LESSONS_LEARNED.md), [CHANGELOG_AI.md](./CHANGELOG_AI.md).

## Layout reminder

| Path | Role |
|------|------|
| `backend/app/main.py` | App + router registration |
| `backend/app/<domain>/` | Engines |
| `backend/app/api/` | HTTP only |
| `backend/tests/` | pytest |

## When changing code

Reuse existing engines. Register new routers. Run `pytest` from `backend/`. Update status/debt docs if behavior or limitations change.
