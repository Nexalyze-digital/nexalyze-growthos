# Nexalyze GrowthOS

Open-source AI Growth Operating System for content, research, publishing, analytics, and automation.

## AI Content Studio

This release includes a working end-to-end AI Content Studio:

- Next.js frontend in `apps/web`
- FastAPI backend in `apps/api`
- Typed content generation request/response
- Ollama local AI provider with deterministic mock fallback
- Copy and regenerate actions in the UI

The default checked-in local configuration documents Ollama through `apps/api/.env.example`. The deterministic mock provider remains available for tests, offline development, and local AI fallback.

See `docs/AI/OLLAMA-INTEGRATION.md` for local inference setup and troubleshooting.

## Apps

- apps/api - FastAPI backend
- apps/web - Next.js frontend
- apps/worker - background jobs

## Local Startup

Backend:

```powershell
.\scripts\run-api.ps1
```

Frontend:

```powershell
.\scripts\run-web.ps1
```

Manual URLs:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend docs: http://localhost:8000/docs

## AI Provider Configuration

The API supports these local provider settings:

```text
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
AI_FALLBACK_PROVIDER=mock
OLLAMA_TIMEOUT_SECONDS=90
```

When Ollama is unavailable, GrowthOS can return deterministic mock content with `provider: "mock-fallback"`.

## Packages

- packages/ai - AI provider abstraction
- packages/auth - authentication utilities
- packages/database - database models and migrations
- packages/prompts - prompt templates
- packages/shared - shared utilities
- packages/ui - shared UI components
