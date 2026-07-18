# Changelog

All notable changes to this project will be documented here.

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
