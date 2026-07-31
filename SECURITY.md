# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.0.0-rc.1 | Yes (best-effort) |
| < 1.0.0-rc.1 | No |

## Reporting a vulnerability

Please **do not** open a public issue for security-sensitive reports.

Preferred path:

1. Open a private GitHub security advisory if available, **or**
2. Contact the repository owner via GitHub with a clear reproduction and impact assessment.

We aim to acknowledge reports within 7 days.

## Current security posture (RC-1)

CodeGraph RC-1 is an open intelligence demo platform:

- **No authentication / authorization** on the HTTP API by default
- Upload paths are keyed by `upload_id` / repository id — treat as single-tenant
- LLM keys (if set) come from environment variables — never commit `.env`
- Integration clients (GitHub/Jira/CI/Slack) are **mock** implementations
- `EXPOSE_ERROR_DETAILS` must remain `false` outside local debugging

## Hardening recommendations before production

- Add API keys / OAuth / reverse-proxy auth
- Sandbox and validate upload extraction paths
- Replace mock integration credentials with a secrets manager
- Run behind TLS termination
- Restrict CORS and rate-limit upload/analysis endpoints
