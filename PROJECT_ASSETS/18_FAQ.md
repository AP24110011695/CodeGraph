# FAQ

**Is the frontend required?**  
No. RC-1 focus is the backend intelligence platform. Frontend is a Vite/React scaffold.

**Do I need OpenAI keys?**  
No. Copilot defaults to a local heuristic provider. Cloud providers activate when keys are set.

**Can I point this at a private monorepo tomorrow?**  
For local analysis yes (upload/index). Multi-tenant production needs auth and durable stores first.

**Why so many packages?**  
Each capability owns one responsibility (SOLID) and stays replaceable behind facades.

**Are GitHub/Jira integrations real?**  
RC-1 clients are mocks for demonstration—labeled in TECH_DEBT.

**Where should AI coding assistants start?**  
`AI_CONTEXT/README_AI.md`.

**How do I contribute?**  
`CONTRIBUTING.md` — reuse engines, register routers, keep tests green.
