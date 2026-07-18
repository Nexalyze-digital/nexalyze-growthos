# Nexalyze GrowthOS

Open-source AI Growth Operating System for content, research, publishing, analytics, and automation.

## AI Content Studio

This release includes a working end-to-end AI Content Studio:

- Next.js frontend in `apps/web`
- FastAPI backend in `apps/api`
- Typed content generation request/response
- Mock content provider with platform, audience, goal, tone, and instruction handling
- Copy and regenerate actions in the UI

The mock provider does not call a cloud or local LLM yet. It is deterministic enough for local testing and keeps the provider architecture ready for a future AI implementation.

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

## Packages

- packages/ai - AI provider abstraction
- packages/auth - authentication utilities
- packages/database - database models and migrations
- packages/prompts - prompt templates
- packages/shared - shared utilities
- packages/ui - shared UI components
