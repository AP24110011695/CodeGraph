# Security

## Reporting

Prefer a private GitHub security advisory, or contact the repo owner directly. Please don’t open a public issue for exploitable bugs.

## RC-1 notes

- No authentication on the API
- Treat as single-tenant / local use
- Keep secrets in `.env` (not committed)
- GitHub/Jira/CI/Slack clients are mocks
- `EXPOSE_ERROR_DETAILS` should stay false outside local debugging

Before any shared deploy: put auth in front, harden uploads, and replace mock credentials.
