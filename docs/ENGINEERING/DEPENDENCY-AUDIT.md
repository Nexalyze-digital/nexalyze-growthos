# Dependency Audit

Status: v0.2.5 foundation review

Commands run:

- `npm outdated --json` in `apps/web`
- `npm audit --omit=dev --json` in `apps/web`
- `.venv\Scripts\python.exe -m pip list --outdated --format=json` in `apps/api`

## Frontend Packages

Current runtime dependencies:

- `next`
- `react`
- `react-dom`
- `lucide-react`
- `clsx`
- `tailwind-merge`
- `class-variance-authority`
- `next-themes`
- `react-hook-form`
- `@hookform/resolvers`
- `zod`

Current development dependencies:

- `typescript`
- `eslint`
- `eslint-config-next`
- `tailwindcss`
- `@tailwindcss/postcss`
- `@types/node`
- `@types/react`
- `@types/react-dom`

## Frontend Freshness

| Package | Current | Wanted | Latest | Recommendation |
| --- | --- | --- | --- | --- |
| `@tailwindcss/postcss` | 4.3.2 | 4.3.3 | 4.3.3 | Patch update in dependency cleanup PR. |
| `eslint` | 9.39.4 | 9.39.5 | 10.7.0 | Patch update is safe candidate; major update needs separate validation. |
| `lucide-react` | 1.23.0 | 1.25.0 | 1.25.0 | Minor update candidate. |
| `react` | 19.2.4 | 19.2.4 | 19.2.7 | Keep pinned until Next compatibility is checked. |
| `react-dom` | 19.2.4 | 19.2.4 | 19.2.7 | Keep paired with `react`. |
| `react-hook-form` | 7.81.0 | 7.82.0 | 7.82.0 | Patch/minor candidate if retained. |
| `tailwindcss` | 4.3.2 | 4.3.3 | 4.3.3 | Patch update in dependency cleanup PR. |
| `typescript` | 5.9.3 | 5.9.3 | 7.0.2 | Do not jump majors without framework validation. |
| `@types/node` | 20.19.43 | 20.19.43 | 26.1.1 | Keep aligned to runtime Node target until the project upgrades Node. |

## Frontend Security

`npm audit --omit=dev` reported two moderate findings:

- `postcss` advisory `GHSA-qx2v-qp2m-jg93`, reachable through Next's bundled dependency path.
- `next` flagged because it depends on the affected PostCSS range.

The reported automatic fix suggested an incompatible downgrade and should not be applied automatically. Track the upstream Next patch path and update Next only after local lint, build, backend integration, and browser validation pass.

## Potentially Unused Frontend Dependencies

Search of `apps/web/src` found active usage of:

- `lucide-react`
- `clsx`
- `tailwind-merge`

Search did not find current runtime usage of:

- `@hookform/resolvers`
- `react-hook-form`
- `zod`
- `next-themes`
- `class-variance-authority`

These may be useful for near-term form validation, theme support, and UI variants. If they are not used by Brand Brain or the next frontend module, remove them in a dedicated dependency cleanup PR.

## Backend Packages

Current Python packages in `requirements.txt`:

- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `pytest`
- `httpx`
- `SQLAlchemy`
- `alembic`

## Backend Freshness

| Package | Current | Latest | Recommendation |
| --- | --- | --- | --- |
| `pip` | 26.1.1 | 26.1.2 | Optional tooling update, not application runtime. |
| `pydantic_core` | 2.46.4 | 2.47.0 | Patch update candidate through the owning `pydantic` dependency. |

No duplicate backend functionality was found in the explicit requirements list.

## v0.5.0 Backend Additions

- `SQLAlchemy` was added for the platform database foundation and workspace-scoped repositories.
- `alembic` was added for versioned schema migration scaffolding.
- No separate JWT or password-hashing dependency was added in v0.5.0; GrowthOS uses Python standard-library HMAC token signing and PBKDF2-HMAC-SHA256 password hashing for the local platform foundation.

## Backend Security

No Python vulnerability scanner is configured in the repository. Add `pip-audit` or an equivalent CI step before adding persistence, authentication, external customer data, or paid provider integrations.

## Recommendations

1. Keep v0.2.0 runtime dependency versions stable for the enterprise foundation PR.
2. Create a later `chore(deps)` PR for safe patch updates.
3. Add automated dependency review in CI.
4. Remove unused frontend dependencies only after confirming they are not needed by Brand Brain.
5. Add Python vulnerability scanning before v0.3.0.
