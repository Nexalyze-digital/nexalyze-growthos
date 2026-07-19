# Changelog

All notable changes to this project will be documented here.

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
