# Publishing Engine Architecture

## Purpose

Publishing Engine turns generated content and research-derived source material into governed, workspace-scoped publishable drafts. v0.6.0 establishes draft lifecycle, review, scheduling, queueing, and mock publishing without real social platform integrations.

## System Boundaries

- Existing Content Studio remains the content generation surface.
- Publishing Engine owns draft persistence, workflow state, review, schedule metadata, and queue metadata.
- Real social API credentials and OAuth flows are out of scope for v0.6.0.
- Browser automation for social posting is explicitly prohibited.

## Backend Layers

- Routes: `app/api/routes/publishing.py`.
- Schemas: `app/schemas/publishing.py`.
- Service: `app/services/publishing_service.py`.
- Repository: `app/repositories/publishing_repository.py`.
- Provider interface: `app/providers/publishing_base.py`.
- Mock provider: `app/providers/publishing_mock.py`.
- Transition policy: service-level deterministic state machine.

## Data Flow

1. Editor creates or saves a draft from Content Studio output.
2. Repository persists draft and initial version in one transaction.
3. Editor edits and creates new draft versions.
4. Editor submits for review.
5. Admin or owner approves, rejects, or requests revision.
6. Approved draft can be scheduled.
7. Schedule creates or updates publishing job.
8. Mock adapter processes queued job and records attempt/result.
9. Audit events link user, workspace, draft, schedule, and job actions.

## Transaction Boundaries

- Draft create: draft + version + audit event.
- Draft update: draft + version + audit event.
- Submit review: draft state + approval record + audit event.
- Approve/reject: approval + comment + draft state + audit event.
- Schedule: schedule + queue job + draft state + audit event.
- Publish attempt: job + attempt + draft state when terminal + audit event.

## Module Dependencies

- Auth/workspace context for ownership and roles.
- Brand Brain for optional brand association.
- Research Hub for optional source material links.
- Content Studio for generated output handoff.
- SQLAlchemy/Alembic for persistence.
- Playwright for browser smoke coverage.

## Future Extensions

- OAuth-backed social connections.
- Real platform adapters.
- Background workers.
- Analytics Hub metrics.
- Workflow Automation triggers.
- Approval policy templates.
