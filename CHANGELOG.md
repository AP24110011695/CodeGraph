# Changelog

## [1.0.0-rc.1] — 2026-07-31

### Added

- Copilot orchestration API (`/copilot/chat`, `/execute`, `/history`)
- Engineering reports, impact analysis, timeline intelligence
- Shared repository path helper
- CI workflow, contributing/security docs

### Fixed

- Registered quality / smells / refactoring routers (had been returning 404)
- Chat “not indexed” test now asserts a real 400 instead of skipping
- Architecture-reasoning errors no longer leak details by default

### Removed

- Old debug chunker scripts and unused smoke scripts under `backend/`

### Changed

- App version `1.0.0-rc.1`; `/` and `/health` include version fields

## Unreleased

- Auth, Redis-backed cache, durable conversation/report stores
- Live git/forge history for timeline
- Production vector store for semantic/RAG

See also `AI_CONTEXT/CHANGELOG_AI.md` for module-by-module notes.
