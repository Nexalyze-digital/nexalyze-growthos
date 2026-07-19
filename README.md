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

## Brand Brain

Brand Brain is the persistent brand memory layer for GrowthOS. It stores company profile, mission, audience, ICP, buyer personas, competitors, voice, tone, offers, proof, URLs, CTAs, hashtags, forbidden phrases, terminology, languages, and regional preferences.

The FastAPI backend exposes Brand Brain CRUD endpoints under `/api/v1/brands` with JSON persistence for the initial implementation. AI Content Studio automatically injects the active Brand Brain profile into content generation requests and returns `brand_context_applied` metadata.

See `docs/AI/BRAND-BRAIN.md` for the architecture, data model, prompt injection strategy, and migration path.

## Research Hub

Research Hub creates structured AI-generated research synthesis from a user brief and optional Brand Brain context. It supports market opportunity, competitor, content, industry trend, customer pain point, and strategic research workflows.

The v0.4.0 implementation does not browse the live web, call external search APIs, scrape websites, or verify sources. Source URLs are preserved only when supplied by the user, and every run includes source notes that disclose whether live research was performed.

Research Hub uses the same local provider posture as Content Studio: Ollama when configured, deterministic mock output for tests/offline use, and mock fallback when the local provider is unavailable.

See `docs/AI/RESEARCH-HUB.md` and `docs/QA/RESEARCH-HUB.md`.

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
