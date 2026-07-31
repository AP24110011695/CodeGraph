# Release Notes — v1.0.0-rc.1

**CodeGraph Release Candidate 1** — first public-ready candidate of the AI Software Architecture Platform.

## Highlights

- Full CG-001…CG-070 intelligence stack on FastAPI  
- Unified Copilot Orchestrator (`/copilot/chat`, `/execute`, `/history`)  
- Timeline, Impact, Engineering Reports  
- Green regression suite (**1221 passed**)  
- MIT license, CONTRIBUTING, SECURITY, CI workflow  
- Portfolio assets under `PROJECT_ASSETS/`

## Install

See root [README.md](./README.md) Quick Start.

## Known limitations

Auth, Redis, live VCS, production vector DB — documented in [AI_CONTEXT/TECH_DEBT.md](./AI_CONTEXT/TECH_DEBT.md).

## Upgrade notes

From earlier development builds: quality/smells/refactoring routes are now registered; root/health include version fields.
