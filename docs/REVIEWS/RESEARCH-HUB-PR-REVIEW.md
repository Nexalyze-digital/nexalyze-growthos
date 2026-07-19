# Research Hub PR Review

Status: release-candidate review for GrowthOS v0.4.0  
Branch: `feature/research-hub-core`  
Recommendation: merge after minor hardening fixes

## Strengths

- Research Hub follows the established GrowthOS enterprise layering: schema, route, service, repository, provider, tests, frontend component, and documentation.
- Provider abstraction is clean and keeps mock and Ollama behavior behind the same contract.
- Brand Brain context is injected before provider execution and marked as protected, highest-priority context.
- Research output is structured into findings, opportunities, risks, recommendations, follow-up questions, and source notes.
- Source-integrity rules are explicit in prompts, mock output, API response notes, UI notices, and documentation.
- JSON persistence has atomic replacement, controlled corruption handling, stable IDs, and temporary-file cleanup.
- Frontend includes empty, loading, success, error, fallback, copy, regenerate, delete, history, desktop, and mobile states.
- Tests cover CRUD, validation, Brand Brain injection, corrupted storage, source URL preservation, Ollama success, sparse model normalization, malformed output, timeout, and connection fallback.
- Playwright smoke coverage validates Research Hub flows in production build mode.

## Risks

- JSON persistence remains single-user/local only. It does not provide cross-process file locking, workspace ownership, authentication, audit logging, or server-side multi-tenant isolation.
- Ollama output quality varies by installed model. The normalizer keeps schema conformance, but synthesis quality still depends on the selected local model.
- Research Hub does not fetch URLs, crawl pages, search externally, or verify citations in v0.4.0.
- Browser smoke tests are local scripts rather than CI-enforced Playwright jobs.
- Frontend state is intentionally local and component-scoped; larger Research Hub workflows will eventually need route-level state and deeper loading/error isolation.

## Architecture Assessment

The implementation is consistent with Brand Brain and AI Content Studio patterns. The FastAPI route layer is thin, service orchestration owns provider execution and fallback, and persistence is isolated behind a repository boundary that can be replaced by a database implementation later.

The current provider contract is intentionally small and appropriate for v0.4.0. It should remain stable enough to support future providers, source fetchers, and multi-agent research steps without leaking provider-specific details into routes or frontend code.

Score: 92/100

## Source-Integrity Assessment

Research Hub v0.4.0 correctly presents itself as AI synthesis only.

Confirmed:

- Prompts forbid live-browsing claims, fabricated citations, fabricated statistics, fabricated named reports, fabricated studies, and fabricated external search.
- User-supplied URLs are preserved in source notes and clearly labeled as supplied but not fetched or verified.
- When no URLs are supplied, the source note discloses AI-generated synthesis.
- UI results include an always-visible no-live-web-research notice.
- Mock and fallback content disclose synthesis-only behavior.
- Findings, recommendations, and source notes are represented as separate fields.

Score: 94/100

## Security Assessment

No secrets, `.env` files, virtual environments, `node_modules`, `.next`, database files, logs, generated reports, encoding backups, or copied third-party source code are included in the branch.

Security posture is appropriate for a local-first release candidate:

- User input is validated with Pydantic length limits and enum constraints.
- Source URLs use typed URL validation.
- Brand Brain context is bounded before prompt injection.
- Provider failures are converted to controlled fallback behavior.
- Storage corruption returns controlled API errors.

Remaining security work belongs to future releases: authentication, workspace ownership, authorization, audit logging, database-level constraints, and server-side rate limiting.

Score: 90/100

## UX Assessment

The Research Hub UI is coherent with the existing GrowthOS shell and uses practical dashboard patterns rather than a marketing layout. It supports:

- Empty state.
- Form validation.
- Brand Brain selection.
- Research history.
- Provider badges.
- Fallback notices.
- Copy, regenerate, and delete actions.
- Mobile navigation.
- Responsive desktop/mobile layouts.

Minor hardening applied during review:

- Brand Brain selector keeps API values clean while displaying readable brand names.
- Regenerate clears stale errors.
- Delete now reports controlled errors if the API request fails.

Score: 90/100

## Testing Assessment

Automated backend coverage is strong for the current scope. Browser smoke coverage exercises the release-critical flows against mock, live Ollama, fallback, and offline states.

Validated:

- Backend tests.
- Frontend lint.
- Frontend production build.
- Research Hub mock flow.
- Research Hub live Ollama flow.
- Research Hub fallback flow.
- Offline state.
- Copy and regenerate.
- Mobile navigation.
- AI Content Studio regression.
- Brand Brain integration through API tests and browser boot path.

Future work should promote the smoke script into first-class CI automation with trace/video artifacts.

Score: 91/100

## Technical Debt

- JSON persistence has no cross-process locking.
- No database migration path is implemented yet.
- No authenticated workspace ownership exists.
- No crawler/search/source-fetching pipeline exists.
- No source-verification confidence scoring exists.
- Playwright smoke tests are not wired into package scripts or CI.
- Research history is global for the local JSON store rather than scoped by workspace/user.

## Recommended Follow-Up Work

- Add database-backed research persistence with workspace ownership.
- Add CI Playwright jobs for Research Hub, Brand Brain, and AI Content Studio regressions.
- Introduce source ingestion behind a strict connector boundary.
- Add source verification, confidence scoring, and citation provenance.
- Add rate limits and request-size monitoring for local provider calls.
- Add route-level Research Hub pages once the workflow grows beyond a single dashboard surface.

## Merge Recommendation

Merge after minor fixes.

The review found no significant architectural blockers. The release candidate is suitable for main after the hardening fixes in this review branch pass validation and are pushed to the PR.
