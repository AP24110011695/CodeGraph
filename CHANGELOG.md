# Changelog

All notable changes to CodeGraph are documented here.  
Detailed AI-oriented history also lives in [`AI_CONTEXT/CHANGELOG_AI.md`](./AI_CONTEXT/CHANGELOG_AI.md).

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Versioning follows SemVer where practical.

## [1.0.0-rc.1] — 2026-07-31

### Added

- Unified Intelligence Orchestrator (Copilot) — CG-070
- Engineering Intelligence Report Generator — CG-069
- Impact Analysis — CG-068
- Timeline Intelligence — CG-067
- Shared repository path resolver (`app.core.paths`)
- RC-1 readiness tests and release documentation
- Portfolio / placement assets under `PROJECT_ASSETS/`

### Fixed

- Registered quality, smells, and refactoring API routers (closed 18 test failures)
- Replaced skipped chat “not indexed” test with a real assertion
- Gated architecture-reasoning error detail behind `EXPOSE_ERROR_DETAILS`

### Removed

- Obsolete `debug_chunker*` scripts
- Empty duplicate `backend/{analyzers,graph,parsers,prompts}` directories
- Manual `backend/test_api.py` / `backend/test_jobs_api.py` smoke scripts

### Changed

- Application version set to `1.0.0-rc.1`
- Root and backend READMEs synchronized with `backend/app/*` layout
- `/` and `/health` return version metadata

## [Unreleased]

- Authentication / multi-tenant isolation
- Redis cache backend and durable conversation stores
- Live VCS history providers for Timeline
- Production vector database for Semantic/RAG

[1.0.0-rc.1]: https://github.com/AP24110011695/CodeGraph/releases/tag/v1.0.0-rc.1
