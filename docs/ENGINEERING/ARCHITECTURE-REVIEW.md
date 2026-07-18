# GrowthOS Architecture Review

Status: v0.2.5 foundation review

## Current Architecture

GrowthOS is currently a small monorepo with a Next.js web app in `apps/web`, a FastAPI service in `apps/api`, shared product and QA documentation in `docs`, and local startup scripts in `scripts`.

The production behavior delivered in v0.2.0 is intentionally narrow:

- A responsive application shell and dashboard.
- AI Content Studio frontend workflows.
- FastAPI content generation and health endpoints.
- AI provider abstraction with Ollama, mock provider, and automatic fallback.
- Backend tests, frontend lint, and frontend production build validation.

## Strengths

- The backend already separates routes, schemas, services, providers, and configuration.
- The AI provider interface is explicit enough to add OpenAI, Anthropic, Gemini, OpenRouter, Groq, and LM Studio without changing route contracts.
- Frontend content studio code is modular across form, status, generated output, API client, constants, and typed content contracts.
- The current feature is covered by backend tests and manual browser validation notes.
- Local `.venv`, `.next`, `node_modules`, caches, database scaffolding, and generated files are ignored and not staged.

## Findings

| Priority | Area | Finding | Recommendation |
| --- | --- | --- | --- |
| P0 | Secrets and generated files | Local generated folders exist, including `.venv`, `.next`, `node_modules`, `__pycache__`, `.pytest_cache`, ignored `db`, ignored `models`, and ignored `alembic` paths. They are not staged. | Keep these ignored. Add a release checklist item to inspect `git status --ignored` before each PR. |
| P1 | Backend module boundaries | Provider abstraction is solid, but future modules will need shared prompt, policy, retry, and telemetry utilities. | Create backend packages for `agents`, `connectors`, `observability`, and `persistence` when the second module begins. |
| P1 | Frontend module boundaries | AI Content Studio owns its own components cleanly, but future modules need shared patterns for module cards, badge states, empty states, and API error handling. | Extract shared UI patterns only after the second module duplicates them. |
| P1 | Data layer | Database docs and ignored scaffolding exist, but the active API is stateless. | Define persistence contracts before Brand Brain: workspaces, brands, documents, research artifacts, generation runs, and provider usage logs. |
| P1 | Testing | Backend tests are meaningful. Frontend has lint and build but no automated component or browser tests yet. | Add Playwright smoke tests for generation, fallback, mobile navigation, and core module pages before v0.3.0 release. |
| P1 | Configuration | Environment variables are documented for provider selection, model, base URL, and frontend API URL. | Introduce typed configuration docs and a checked-in `.env.example` if it is not already present in a future PR. Never commit real `.env` files. |
| P2 | Dependency footprint | Several frontend packages appear unused in current `src`: `react-hook-form`, `@hookform/resolvers`, `zod`, `next-themes`, and `class-variance-authority`. | Keep temporarily if they are planned for near-term forms/theme work; otherwise remove in a dedicated dependency cleanup PR. |
| P2 | Documentation topology | Root docs are useful but mixed between product, database, architecture, QA, and engineering. | Continue grouping by `docs/AI`, `docs/ARCHITECTURE`, `docs/ENGINEERING`, `docs/QA`, `docs/api`, `docs/database`, and `docs/product`. |

## Duplicate Code

No high-risk duplicate runtime implementation was found. Current repetition is mostly expected for early UI composition and should remain until another module proves the abstraction.

Potential future candidates:

- Provider badge and offline status display.
- Module navigation metadata.
- Form field state and validation handling.
- Backend health/provider capability checks.

## Dead Code And Unused Assets

No tracked dead code requiring immediate removal was verified.

Observed local-only generated artifacts:

- `apps/api/.venv`
- `apps/api/.pytest_cache`
- `apps/api/**/__pycache__`
- `apps/web/.next`
- `apps/web/node_modules`
- `apps/web/next-env.d.ts`

These are ignored and should not be committed.

## Modularization Roadmap

1. Keep the v0.2.0 implementation stable until Brand Brain forces a second module boundary.
2. Add shared frontend module primitives after duplicate UI appears in Brand Brain.
3. Add backend domain packages for brands, research, publishing, analytics, and workflow automation.
4. Introduce persistence only with explicit migration and rollback documentation.
5. Add provider telemetry and generation run logging before paid cloud providers.

## Release Guidance

No behavior-changing refactor is recommended for v0.2.5. The highest value foundation work is documentation, testing strategy, dependency hygiene, and module contracts.
