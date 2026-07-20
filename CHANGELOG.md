# Changelog

All notable changes to this project will be documented here.

## 0.6.0 Unreleased

- Added Publishing Engine backend foundation with drafts, draft versions, approvals, approval comments, schedules, publishing jobs, publishing attempts, and workspace publishing settings.
- Added Alembic migration for Publishing Engine persistence.
- Added workspace-scoped Publishing API endpoints for draft CRUD, review, scheduling, and queue operations.
- Added service and repository layers with role authorization, audit events, optimistic revision checks, version-pinned scheduling, and idempotent queueing.
- Added backend tests for publishing CRUD, authorization, workspace isolation, lifecycle transitions, scheduling, queue validation, retry, and archive/restore.
- Added responsive Publishing frontend workflows for library, editor, detail, review, calendar, queue, settings, and connection status.
- Added Content Studio save-to-draft handoff.
- Added Playwright smoke coverage for Publishing frontend workflows.
- Added deterministic mock publishing processing for LinkedIn, X, Instagram, and Facebook.
- Added durable queue states for processing, published, retry pending, dead letter, failed, and cancelled jobs.
- Added workspace publishing processing settings, exponential retry scheduling, dead-letter handling, and publishing audit history.
- Added backend tests for processing success, transient retries, permanent failures, settings authorization, audit history, and workspace isolation.
- Real external publishing providers, OAuth, browser automation, and social API credentials remain out of scope.

## 0.5.1

- Validated Alembic upgrade, downgrade, and re-upgrade against local PostgreSQL 17.
- Added PostgreSQL driver support and SQLAlchemy pool pre-ping configuration.
- Added PostgreSQL backup and restore helper scripts for test databases.
- Hardened frontend session handling with automatic access-token refresh and one-time request retry.
- Added role-aware frontend hiding for viewer write controls.
- Added CI-ready Playwright smoke workflow using mock provider and local test database.
- Documented PostgreSQL validation, backup/restore, token-storage risks, release review, and handoff.

## 0.5.0

- Added authentication with registration, login, logout, access tokens, refresh tokens, password hashing, and current-user endpoint.
- Added organizations, workspaces, memberships, roles, and workspace switcher.
- Added SQLAlchemy 2.x database foundation with Alembic scaffolding.
- Added workspace-scoped Brand Brain and Research Hub persistence.
- Added JSON migration utility with dry-run, backup, and live local migration support.
- Added audit events for authentication and protected data changes.
- Protected Brand Brain, Research Hub, and AI Content Studio behind authenticated workspace context.
- Scoped CORS headers and methods to GrowthOS API needs.

## 0.4.0

- Added Research Hub core for structured AI-generated research synthesis.
- Added research schemas, CRUD/regenerate API, service layer, provider layer, and JSON persistence.
- Added Ollama and deterministic mock research providers with mock fallback.
- Added Brand Brain context injection for research runs.
- Added source-note handling that discloses no live web research is performed.
- Added responsive Research Hub UI with history, results, copy, regenerate, delete, provider badges, and fallback notices.
- Added backend tests and QA documentation for Research Hub.

## 0.3.0

- Added Brand Brain core with JSON-backed persistence.
- Added Brand Brain CRUD API, validation, repository layer, and service layer.
- Added Brand Brain dashboard, profile editor, voice editor, persona/product/competitor managers, and preview panel.
- Injected active Brand Brain context into AI Content Studio generation requests.
- Added tests for Brand Brain CRUD, validation, and AI prompt injection.
- Documented Brand Brain architecture, adoption patterns, and future database migration path.

## 0.2.5

- Established the enterprise engineering foundation.
- Added architecture review, global skills integration, open-source catalog, dependency audit, coding standards, module blueprints, and AI provider roadmap.
- Confirmed no runtime functionality changes in the foundation release.

## 0.1.1

- Delivered the end-to-end AI Content Studio release.
- Added modular Next.js components for the GrowthOS shell, dashboard, form, and generated output.
- Added FastAPI content routes, schemas, service layer, and mock provider.
- Added backend tests, local environment examples, QA documentation, and startup scripts.
- Documented that content generation uses a mock provider and does not call a cloud or local LLM yet.

## 0.1.2

- Added a local Ollama content provider behind the existing provider abstraction.
- Preserved deterministic mock generation for tests, offline development, and fallback.
- Added provider status in `/health` and provider badges in generated output.
- Documented Ollama setup, environment variables, fallback behavior, and privacy notes.

## 0.1.0

- Initial repository structure
- Added governance files
- Added roadmap and documentation placeholders
