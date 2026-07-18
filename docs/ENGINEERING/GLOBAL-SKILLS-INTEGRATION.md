# Global Skills Integration

Status: v0.2.5 foundation review

GrowthOS can use the global engineering skills installed on this machine as repeatable operating procedures. These skills should guide implementation and review; they should not replace the repository's own code, tests, or documented release process.

## Applicable Skills

| Skill | Use In GrowthOS | Future Modules | Invocation Timing |
| --- | --- | --- | --- |
| `nexalyze-global-engineering` | Project discovery, standards alignment, validation checklist, release readiness. | All modules. | Start of each feature, before architecture changes, before release. |
| `nexalyze-global-code-quality` | Maintainability review, duplication detection, modularity checks, code review posture. | All modules. | Before refactors, before PR review, after test failures. |
| `nexalyze-global-react` | Next.js and React component patterns, state boundaries, component ergonomics. | Brand Brain, Research Hub, Publishing, Analytics, Proposal Generator, Presentation Builder. | Before frontend feature work. |
| `nexalyze-global-accessibility` | Keyboard access, responsive behavior, ARIA, focus states, contrast. | All user-facing modules. | During UI implementation and QA. |
| `nexalyze-global-playwright` | Browser validation, screenshot review, mobile checks, console checks. | AI Content Studio, Brand Brain, Publishing, Analytics. | After UI changes and before release. |
| `nexalyze-global-security` | Secrets handling, dependency review, auth and data protection posture. | Brand Brain, Publishing, Website Intelligence, Lead Intelligence, Workflow Automation. | Before adding persistence, external APIs, or auth. |
| `nexalyze-global-performance` | Frontend build health, runtime performance, bundle awareness. | Dashboard, Analytics, Website Intelligence, Presentation Builder. | After adding heavy UI, data views, or media. |
| `nexalyze-global-seo` | Technical SEO and structured metadata for public-facing surfaces. | Website Intelligence, Publishing, public reports. | Before public pages or generated content outputs. |
| `nexalyze-global-aeo` | Answer engine optimization strategy. | Content Studio, Research Hub, Website Intelligence. | Before content intelligence and research deliverables. |
| `nexalyze-global-geo` | Generative engine optimization and entity clarity. | Brand Brain, Research Hub, Website Intelligence. | Before brand/entity intelligence features. |
| `nexalyze-global-schema` | Structured data contracts and schema validation. | Brand Brain, Research Hub, Analytics, Proposal Generator. | Before adding stored data or cross-module payloads. |
| `nexalyze-global-content` | Content quality, editorial consistency, documentation clarity. | Content Studio, Publishing, Proposal Generator, Presentation Builder. | During content workflow and docs work. |
| `nexalyze-global-production-release` | Release validation, changelog hygiene, rollback planning. | All release trains. | Final PR and release candidate validation. |

## Non-Nexalyze Skill Groups

| Skill Area | GrowthOS Use |
| --- | --- |
| `testing-accessibility-qa` | Cross-check Playwright, accessibility, Lighthouse, and regression strategy. |
| `ui-ux-design-systems` | Reference UI system decisions without importing a large component library by default. |
| `workflow-automation` | Shape Workflow Automation module patterns and n8n-style orchestration concepts. |
| `llm-application-platform` | Reference agent routing, tool orchestration, prompt management, and provider abstraction. |
| `seo-aeo-geo` | Supplement Nexalyze SEO/AEO/GEO skills for research and website intelligence. |
| `security` | Supplement secret scanning and dependency risk practices. |
| `performance-build` | Supplement build tooling, bundle review, and web vital analysis. |

## Recommended Invocation Workflow

1. Start every feature with `nexalyze-global-engineering` for discovery and acceptance criteria.
2. Use the domain skill next, such as React, security, performance, content, schema, or SEO.
3. Implement the smallest functional change that satisfies the module objective.
4. Run repo-native checks first: backend tests, frontend lint, frontend build.
5. Use `nexalyze-global-playwright` for browser workflows and responsive validation.
6. Use `nexalyze-global-code-quality` before opening the PR.
7. Use `nexalyze-global-production-release` before merge or tag creation.

## Standards To Adopt

- Prefer repository patterns over generic skill examples.
- Do not copy third-party code from skill reference repositories.
- Treat skill output as guidance, then validate through GrowthOS tests.
- Document new module contracts before adding cross-module dependencies.
- Keep release checklists concrete: commands run, results observed, limitations, and rollback notes.
