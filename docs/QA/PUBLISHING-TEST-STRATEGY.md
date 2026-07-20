# Publishing Test Strategy

## Backend Tests

- Draft create, list, get, update, duplicate, archive, restore, soft delete.
- Workspace isolation for every draft, schedule, job, and connection query.
- Role enforcement for viewer, editor, admin, owner.
- Lifecycle state transitions and invalid transition `409`.
- Version history on create, update, duplicate.
- Review submit, approve, reject, request revision, comments, history.
- Self-approval prevention when enabled.
- Approval not required when workspace setting disables it.
- Scheduling validation, timezone conversion, past-time rejection.
- Conflict detection.
- Queue idempotency and retry count.
- Transient mock failure and retry success.
- Permanent mock failure blocks retry.
- Publishing attempt history.
- Audit events for write actions.
- Alembic upgrade and downgrade on SQLite and PostgreSQL.

## Frontend Tests

- Draft creation from generated Content Studio output.
- Draft editor save and validation errors.
- Content Library search, filter, sort, pagination, archived view.
- Review Queue approve/reject/revision request states.
- Calendar month, week, day render.
- Schedule, reschedule, unschedule interactions.
- Queue pending, processing, succeeded, failed, cancelled views.
- Role-aware controls.
- Mobile navigation.
- API offline states.
- Accessible labels, keyboard operation, focus order, and perceivable status messages.

## Playwright Smoke

- Editor creates draft.
- Editor submits for review.
- Admin approves.
- Viewer cannot edit.
- Admin schedules.
- Mock publish succeeds.
- Mock publish fails transiently and retries.
- Mock publish permanent failure surfaces safe error summary.
- Calendar renders correctly.
- Content Studio regression.
- Brand Brain regression.
- Research Hub regression.
- No unexpected console errors.

## Validation Gates

- `python -m pytest tests`
- PostgreSQL migration validation.
- `npm run lint`
- `npm run build`
- Playwright smoke.
- Secret scan.
- Forbidden artifact review.
