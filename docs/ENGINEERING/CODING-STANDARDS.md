# GrowthOS Coding Standards

Status: v0.2.5 foundation standard

## Frontend

- Use Next.js App Router conventions already present in `apps/web`.
- Keep feature components in module folders such as `components/content-studio`.
- Keep shared UI primitives in `components/ui`.
- Keep API clients in `src/lib` and typed payloads in `src/types`.
- Prefer small, named components over large page files.
- Preserve responsive behavior and mobile navigation for every user-facing module.
- Use icons for compact tool actions when a recognizable icon exists.

## Backend

- Use FastAPI route modules under `app/api/routes`.
- Keep request and response contracts in `app/schemas`.
- Keep orchestration in `app/services`.
- Keep external AI or service integrations behind provider or connector interfaces.
- Keep configuration in `app/core/config.py`.
- Avoid importing provider SDKs directly inside route handlers.

## API

- Version public API routes under `/api/v1`.
- Return typed response shapes with explicit provider and fallback metadata when AI is involved.
- Validate request payloads with Pydantic.
- Use clear HTTP status codes and actionable error messages.
- Do not expose secrets, local paths, stack traces, or raw provider errors to frontend users.

## Testing

- Backend: use pytest and FastAPI test clients for routes and service behavior.
- Frontend: lint and production build are required for every PR.
- Browser workflows: validate generation, regenerate, copy, fallback, mobile layout, and console errors.
- Add Playwright smoke coverage before the next user-facing module reaches release candidate status.
- Tests must be deterministic by default; live provider tests should be clearly separated from mock tests.

## Documentation

- Store engineering process docs in `docs/ENGINEERING`.
- Store system and module architecture in `docs/ARCHITECTURE`.
- Store provider and AI operations docs in `docs/AI`.
- Store QA evidence in `docs/QA`.
- Keep docs factual, dated by release context, and aligned with tested behavior.

## Git Workflow

- Branch names should use `feature/`, `fix/`, `docs/`, or `chore/`.
- Use conventional commit messages.
- Commit only intentional source, test, or documentation changes.
- Never stage `.env`, `.venv`, `node_modules`, `.next`, database files, generated caches, encoding backups, or secrets.
- Review `git status --short --ignored` before release PRs.

## Naming Conventions

- React components: `PascalCase`.
- Hooks and helpers: `camelCase`.
- TypeScript types and interfaces: `PascalCase`.
- Python modules: `snake_case`.
- Python classes: `PascalCase`.
- Environment variables: `UPPER_SNAKE_CASE`.
- API JSON fields: `snake_case` unless compatibility requires otherwise.

## Error Handling

- Frontend should map API failure states to visible, calm user states.
- Backend should catch provider-level failures and return controlled fallback behavior where designed.
- Preserve mock fallback for AI generation until a product decision removes it.
- Log enough context to debug provider failures without logging secrets or full user payloads.

## Logging

- Do not use ad hoc debug output in committed code.
- Prefer structured server logs when logging is introduced.
- Include provider name, route, request class, and fallback status for AI operations.
- Do not log API keys, tokens, full prompts, customer secrets, or personal data.

## Configuration

- Configure local values through environment variables.
- Check in examples, not real secrets.
- Keep frontend-exposed variables limited to safe `NEXT_PUBLIC_*` values.
- Document defaults and fallback order when adding providers or connectors.

## Accessibility

- Every interactive element must be keyboard reachable.
- Form fields require labels and accessible error text.
- Loading, empty, success, error, and fallback states must be perceivable.
- Validate mobile layouts before release.

## Performance

- Keep initial module pages lightweight.
- Avoid adding heavy UI or agent libraries to the frontend unless needed at runtime.
- Prefer server-side provider calls.
- Watch production build output and bundle changes after dependency updates.

## Security

- Treat all provider output as untrusted text.
- Do not render generated content as raw HTML unless sanitized.
- Keep CORS scoped to expected local and deployed frontend origins.
- Add secret scanning and dependency vulnerability scanning before handling production customer data.
- Review external integrations for scopes, rate limits, data retention, and failure modes.
