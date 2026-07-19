# GrowthOS Product Bible

## Brand Brain Core

Brand Brain is the first enterprise capability after the v0.2.5 foundation. It provides persistent brand memory for all AI-assisted workflows.

### Requirements

- Store company profile, brand name, mission, vision, core values, products and services, industry, target audience, ICP, buyer personas, competitors, brand voice, tone guidelines, writing style, value propositions, proof points, case studies, website URLs, social URLs, preferred CTAs, preferred hashtags, forbidden phrases, preferred terminology, languages, and regional preferences.
- Provide CRUD APIs with validation.
- Persist data locally as JSON for the initial implementation.
- Keep repository and service boundaries ready for database migration.
- Provide a dashboard, editors, managers, and preview panel in the GrowthOS UI.
- Automatically apply active Brand Brain context to AI Content Studio generation.
- Expose response metadata so users and tests can confirm Brand Brain was applied.

### Acceptance Criteria

- Users can create, update, view, and delete a Brand Brain profile.
- Content generation includes Brand Brain context when a profile exists.
- Generated output identifies when Brand Brain was applied.
- Existing AI Content Studio generation, copy, regenerate, validation, and fallback workflows continue to work.

## Research Hub Core

Research Hub is the v0.4.0 enterprise capability for structured AI-generated research synthesis. It turns a topic, objective, audience, industry, geography, research type, depth, optional source URLs, and optional Brand Brain profile into a saved research run.

### Requirements

- Support market opportunity, competitor analysis, content opportunity, industry trends, customer pain points, and strategic research.
- Support Quick, Standard, and Deep depth settings.
- Generate executive summary, key findings, opportunities, risks, recommendations, follow-up questions, and source notes.
- Preserve source URLs only when supplied by the user.
- Clearly disclose that no live web research or source verification is performed in v0.4.0.
- Persist research runs locally as JSON with atomic writes and corruption handling.
- Provide list, retrieve, delete, and regenerate workflows.
- Use Brand Brain context when selected.
- Support Ollama, mock, and mock-fallback provider states.

### Acceptance Criteria

- Users can create, view, regenerate, delete, and copy research runs.
- Research history persists locally.
- Source notes distinguish user-supplied URLs from AI-generated synthesis.
- Existing Brand Brain and AI Content Studio workflows continue to work.
- The UI remains responsive and accessible across desktop and mobile.

## Platform Identity, Workspaces, And Database

GrowthOS v0.5.0 establishes the multi-user platform foundation required before Publishing Engine and other collaborative modules.

### Requirements

- Support user registration, login, logout, current user, access tokens, refresh tokens, token expiry, password hashing, password validation, and account activation status.
- Support organizations, workspaces, memberships, and roles: owner, admin, editor, viewer.
- Protect frontend routes behind authentication.
- Persist session state locally in the browser.
- Scope Brand Brain, Research Hub, and AI context lookup to the active workspace.
- Add SQLAlchemy 2.x persistence and Alembic migration scaffolding.
- Support SQLite for local/test usage and PostgreSQL configuration for production.
- Provide JSON migration dry-run and live migration with backup.
- Add audit events for login and data changes.
- Preserve Ollama and mock fallback provider support.

### Acceptance Criteria

- Users can register, log in, refresh tokens, log out, and view current-user/workspace context.
- Workspace members can only access data in their authorized workspace.
- Viewers cannot perform write actions.
- Brand Brain and Research Hub remain functional after database migration.
- Existing AI Content Studio workflows continue to work with workspace-scoped Brand Brain context.
- Backend tests, frontend lint, frontend build, Playwright smoke, and migration validation pass.
