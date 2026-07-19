# Research Hub Implementation Plan

Status: v0.4.0 planning only

This plan does not implement Research Hub. It defines the intended architecture, scope, risks, and validation path for the next GrowthOS enterprise capability.

## Objectives

- Build a Research Hub that turns a topic, market, competitor, or customer question into structured research artifacts.
- Reuse Brand Brain context to keep research aligned with the saved company profile, ICP, audience, terminology, and positioning.
- Support local-first AI validation through Ollama and deterministic mock workflows.
- Create a foundation for future Website Intelligence, Proposal Generator, Lead Intelligence, and Publishing workflows.

## User Stories

- As a founder, I want to research a market topic so I can understand opportunities before creating content or offers.
- As a marketer, I want competitor summaries so I can differentiate messaging against known alternatives.
- As a strategist, I want research findings connected to Brand Brain so recommendations match our ICP and voice.
- As an operator, I want saved research runs so I can reuse findings in proposals, content, and campaigns.
- As a reviewer, I want source notes and confidence labels so I can separate facts from AI interpretation.

## Functional Requirements

- Create a research run from topic, audience, objective, and optional source URLs.
- Load active Brand Brain context into research prompts.
- Generate structured outputs: summary, key findings, opportunities, risks, suggested content angles, and follow-up questions.
- Persist research runs and artifacts locally using JSON initially.
- Return provider metadata and fallback status.
- Provide a dashboard panel for recent research runs.
- Provide empty, loading, error, offline, and result states.
- Keep generated research text rendered as plain text, not raw HTML.

## Technical Architecture

- Backend schemas: `ResearchRunCreate`, `ResearchRun`, `ResearchArtifact`, `ResearchFinding`, `ResearchSource`.
- Backend routes: `POST /api/v1/research/runs`, `GET /api/v1/research/runs`, `GET /api/v1/research/runs/{id}`, `DELETE /api/v1/research/runs/{id}`.
- Service layer: coordinates Brand Brain context, provider calls, source normalization, and artifact persistence.
- Repository layer: JSON-backed `ResearchRepository` with atomic writes and corruption handling from the Brand Brain pattern.
- Provider layer: reuse existing content provider concepts, but introduce research-specific prompt builders and response schemas.
- Frontend: Research Hub dashboard, run form, findings view, source notes, and export-ready summary panel.

## AI Agent Responsibilities

- Research planner: turns a user topic into a focused research brief.
- Source evaluator: assesses relevance and flags missing source context.
- Insight synthesizer: groups findings into opportunities, risks, and content angles.
- Brand alignment reviewer: checks whether findings match Brand Brain ICP, voice, and positioning.
- Follow-up question generator: suggests the next research questions.

## Integration With Brand Brain

- Research prompts should include active Brand Brain context as protected context.
- Outputs should explicitly reference the intended ICP, audience, value propositions, and competitors when present.
- Research artifacts should record which Brand Brain profile was applied.
- Future versions should allow comparing research output across multiple brand profiles.

## Integration With Ollama

- Ollama remains the preferred local live provider for v0.4.0 validation.
- Research prompts must request structured JSON where possible.
- Mock fallback should return deterministic research artifacts for tests and offline demos.
- Research runs should expose `provider`, `brand_context_applied`, and `fallback_used` metadata.
- Prompt size must be bounded because research prompts can grow quickly.

## Open Source Catalog Opportunities

No code should be copied from these repositories. The useful accelerators are patterns and concepts:

| Repository | Use For Research Hub | Integration Approach |
| --- | --- | --- |
| `run-llama__llama_index` | Retrieval, document chunking, and research memory concepts | Use as an architecture reference for future indexed research artifacts |
| `deepset-ai__haystack` | Search/retrieval pipeline concepts | Use as a reference for source evaluation and retrieval stages |
| `microsoft__markitdown` | File-to-Markdown conversion concepts | Consider as a future dependency for document ingestion after license and dependency review |
| `browser-use__browser-use` | Browser research automation concepts | Use as a reference for later Website Intelligence and source-gathering workflows |
| `microsoft__playwright` | Browser validation and future source capture | Use for formal browser tests and possible controlled page inspection |
| `modelcontextprotocol__python-sdk` | Tool boundary concepts | Use as a future connector/tool interface reference |
| `openai__openai-agents-python` | Agent responsibility separation | Use as a reference for planner/evaluator/synthesizer boundaries |

## External Services

Initial v0.4.0 should not require paid external services.

Possible future services:

- Search API for source discovery.
- Browser automation for controlled source inspection.
- Vector database for research memory.
- Cloud LLM provider for higher-quality synthesis.
- CRM or analytics integrations for account-specific research.

## Risks

- Generated research can sound authoritative without verified sources.
- Local models may produce inconsistent JSON for complex research prompts.
- Source URLs can introduce SSRF/security risks if fetched server-side without controls.
- JSON persistence will not support multi-user concurrency.
- Browser automation and scraping can create legal, rate-limit, and reliability issues.
- Brand Brain context can bias research too strongly if the prompt does not separate fact from recommendation.

## Phased Implementation Plan

### Phase 1: Local Research Core

- Add schemas, repository, service, and CRUD/list routes.
- Add deterministic mock research provider.
- Inject Brand Brain context.
- Add backend tests for create/list/get/delete, validation, and Brand Brain injection.

### Phase 2: Frontend Research Hub

- Add Research Hub dashboard section.
- Add research run form.
- Add findings, opportunities, risks, and follow-up question panels.
- Add loading, empty, error, offline, and mobile states.

### Phase 3: Live Ollama Validation

- Add research prompt builder for Ollama.
- Validate structured JSON parsing and fallback.
- Add prompt size guardrails.
- Record provider metadata in research artifacts.

### Phase 4: Source Handling

- Add optional source URL input and validation.
- Store source notes without fetching arbitrary URLs by default.
- Define a safe source-fetching policy before live crawling.

### Phase 5: Automation And CI

- Add Playwright regression for Content Studio, Brand Brain, and Research Hub.
- Add docs for local startup, validation, and known limitations.
- Prepare follow-up issues for database persistence and workspace ownership.

## Estimated Development Phases

- Phase 1: 1 implementation PR.
- Phase 2: 1 frontend PR.
- Phase 3: 1 provider-validation PR.
- Phase 4: 1 source-policy and ingestion PR.
- Phase 5: 1 test automation PR.

## Testing Strategy

- Backend unit tests for schema validation, repository writes, corrupted JSON handling, and service orchestration.
- API tests for research run CRUD and provider fallback.
- Prompt injection tests to confirm Brand Brain priority and bounded prompt size.
- Mock provider tests for deterministic results.
- Ollama live validation for at least one market topic and one competitor topic.
- Frontend lint and production build.
- Browser regression for create research run, view results, mobile layout, offline state, and no connected-console errors.
- Regression checks for AI Content Studio and Brand Brain after Research Hub is added.
