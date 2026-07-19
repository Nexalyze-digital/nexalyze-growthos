# GrowthOS Module Blueprints

Status: v0.2.5 foundation blueprint

## Shared Platform Pattern

Each module should use the same high-level flow:

1. Frontend module captures validated user input.
2. Frontend API client calls a versioned FastAPI endpoint.
3. Backend route validates with Pydantic schemas.
4. Service layer coordinates providers, connectors, persistence, and policy.
5. Provider or connector layer calls AI models or external services.
6. Response returns typed output, status, provider metadata, and fallback information.
7. Optional persistence records artifacts, usage, audit events, and workflow state.

## Brand Brain

- Responsibilities: brand profile, voice, positioning, audience segments, offers, proof points, objections, and reusable messaging rules.
- APIs: `GET /api/v1/brands`, `POST /api/v1/brands`, `GET /api/v1/brands/{id}`, `POST /api/v1/brands/{id}/analyze`.
- Data flow: user inputs brand facts; AI generates structured brand intelligence; approved brand assets feed content, proposals, and research.
- Dependencies: AI provider layer, persistence, schema validation, document import.
- Future AI agents: brand strategist, voice analyst, competitor interpreter.
- External integrations: website crawler, document upload, CRM import, social profile import.

## Research Hub

- Responsibilities: market research, competitor research, source summaries, citation-ready findings, content opportunities.
- APIs: `POST /api/v1/research/runs`, `GET /api/v1/research/runs`, `GET /api/v1/research/runs/{id}`, `DELETE /api/v1/research/runs/{id}`, `POST /api/v1/research/runs/{id}/regenerate`.
- Data flow: topic and optional user-supplied source URLs enter backend; Brand Brain context is injected when selected; AI synthesizes structured findings; artifacts are stored in JSON for v0.4.0.
- Dependencies: Brand Brain, provider layer, JSON persistence, source-note validation.
- Future AI agents: researcher, source evaluator, insight synthesizer.
- External integrations: future web search, Crawl4AI, Playwright, RSS, file conversion, and vector search. None are active in v0.4.0.

## Publishing

- Responsibilities: campaign planning, channel formatting, scheduling metadata, approval workflow.
- APIs: `POST /api/v1/publishing/drafts`, `POST /api/v1/publishing/schedules`, `GET /api/v1/publishing/calendar`.
- Data flow: approved content becomes drafts; platform constraints validate format; publishing state is tracked through approval and scheduling.
- Dependencies: Brand Brain, Content Studio, provider layer, persistence, social connectors.
- Future AI agents: channel editor, compliance reviewer, calendar optimizer.
- External integrations: LinkedIn, X, Instagram, Facebook, scheduling platforms.

## Website Intelligence

- Responsibilities: website audits, SEO/AEO/GEO analysis, conversion opportunities, technical recommendations.
- APIs: `POST /api/v1/websites/audits`, `GET /api/v1/websites/audits/{id}`, `POST /api/v1/websites/crawl`.
- Data flow: URL enters crawler; diagnostics collect page metadata and performance signals; AI produces prioritized recommendations.
- Dependencies: browser automation, Lighthouse-style audits, SEO schema tools, provider layer.
- Future AI agents: technical SEO analyst, CRO analyst, answer engine analyst.
- External integrations: browser automation, Lighthouse, sitemap parsing, analytics platforms.

## Lead Intelligence

- Responsibilities: lead enrichment, account summaries, fit scoring, outreach context.
- APIs: `POST /api/v1/leads/enrich`, `GET /api/v1/leads/{id}`, `POST /api/v1/leads/{id}/brief`.
- Data flow: lead/account input is normalized; enrichment connectors and research agents gather context; service computes score and recommended actions.
- Dependencies: Brand Brain, Research Hub, persistence, privacy policy.
- Future AI agents: account researcher, qualification analyst, outreach planner.
- External integrations: CRM, LinkedIn, website crawler, enrichment providers.

## Analytics

- Responsibilities: dashboards, KPI definitions, content performance, provider usage, module adoption metrics.
- APIs: `GET /api/v1/analytics/overview`, `GET /api/v1/analytics/content`, `GET /api/v1/analytics/providers`.
- Data flow: events and artifacts are aggregated; backend returns summarized metrics; frontend renders dashboards and drilldowns.
- Dependencies: event logging, persistence, chart components, performance standards.
- Future AI agents: KPI analyst, anomaly detector, reporting assistant.
- External integrations: website analytics, social APIs, CRM, ad platforms.

## Proposal Generator

- Responsibilities: proposal drafts, scopes, pricing narratives, executive summaries, proof sections.
- APIs: `POST /api/v1/proposals`, `GET /api/v1/proposals/{id}`, `POST /api/v1/proposals/{id}/regenerate-section`.
- Data flow: Brand Brain and Research Hub inputs combine with user scope; AI produces proposal sections; user edits and exports.
- Dependencies: Brand Brain, Research Hub, provider layer, document export.
- Future AI agents: proposal strategist, scope writer, objection handler.
- External integrations: document export, CRM opportunity data, pricing systems.

## Presentation Builder

- Responsibilities: deck outlines, slide copy, speaker notes, visual structure, export handoff.
- APIs: `POST /api/v1/presentations`, `GET /api/v1/presentations/{id}`, `POST /api/v1/presentations/{id}/slides`.
- Data flow: proposal or research artifacts become slide outlines; AI creates slide content; frontend supports review and export.
- Dependencies: Proposal Generator, Research Hub, provider layer, media assets.
- Future AI agents: presentation strategist, slide editor, visual reviewer.
- External integrations: PowerPoint export, Google Slides, image generation, brand asset library.

## Workflow Automation

- Responsibilities: cross-module automations, triggers, approvals, schedules, connector actions.
- APIs: `POST /api/v1/workflows`, `GET /api/v1/workflows/{id}`, `POST /api/v1/workflows/{id}/runs`.
- Data flow: user defines trigger and steps; workflow engine executes module actions and connector calls; audit trail records each run.
- Dependencies: all modules, connector registry, permissions, event logging.
- Future AI agents: workflow planner, connector operator, run monitor.
- External integrations: n8n-style services, email, calendar, CRM, social platforms, MCP tools.
