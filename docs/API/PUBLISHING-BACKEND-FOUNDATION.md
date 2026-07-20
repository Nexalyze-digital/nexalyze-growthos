# Publishing Backend Foundation API

Base path: `/api/v1/publishing`

All endpoints require authentication. Every response is scoped to the active workspace from the access token or `X-Workspace-Id` header. Frontend role-aware controls are advisory only; backend authorization is authoritative.

## Drafts

- `POST /drafts`: create a workspace draft. Roles: editor, admin, owner.
- `GET /drafts`: list drafts with search, platform, status, archived, page, and page size filters. Roles: viewer, editor, admin, owner.
- `GET /drafts/{draft_id}`: read one draft in the active workspace.
- `PUT /drafts/{draft_id}`: update a draft and create a new version. Requires `expected_revision` for optimistic conflict detection. Roles: editor, admin, owner.
- `POST /drafts/{draft_id}/duplicate`: duplicate an existing draft. Roles: editor, admin, owner.
- `POST /drafts/{draft_id}/archive`: archive a draft. Roles: editor, admin, owner.
- `POST /drafts/{draft_id}/restore`: restore an archived draft. Roles: editor, admin, owner.
- `GET /drafts/{draft_id}/versions`: list version history.

## Review

- `POST /drafts/{draft_id}/submit`: submit generated, edited, or rejected draft for review. Roles: editor, admin, owner.
- `POST /drafts/{draft_id}/approve`: approve a pending review. Roles: admin, owner.
- `POST /drafts/{draft_id}/reject`: reject a pending review with comment. Roles: admin, owner.
- `POST /drafts/{draft_id}/request-revision`: request revision with comment. Roles: admin, owner.
- `POST /approvals/{approval_id}/comments`: add an approval comment. Roles: editor, admin, owner.
- `GET /drafts/{draft_id}/review-history`: list approvals and comments.

Self-approval is blocked by default through `workspace_publishing_settings.prevent_self_approval`.

## Scheduling

- `POST /drafts/{draft_id}/schedule`: schedule an approved draft. Roles: admin, owner.
- `PUT /schedules/{schedule_id}`: reschedule a scheduled item. Roles: admin, owner.
- `POST /schedules/{schedule_id}/unschedule`: unschedule and return the draft to approved state. Roles: admin, owner.

Schedules store `scheduled_at_utc`, the submitted workspace timezone, and a pinned approved `draft_version_id`.

## Publishing Queue

- `POST /drafts/{draft_id}/enqueue`: create or reuse an idempotent pending queue job for an approved or scheduled draft. Roles: admin, owner.
- `GET /jobs`: list queue jobs for the workspace.
- `GET /jobs/{job_id}`: get job detail and attempt history.
- `POST /jobs/process-next`: process the next due pending or retry-pending jobs using the deterministic mock provider. Roles: admin, owner.
- `POST /jobs/{job_id}/process`: process a single due pending or retry-pending job. Roles: admin, owner.
- `POST /jobs/{job_id}/retry`: manually retry failed, retry-pending, or dead-letter transient jobs that have retry budget remaining. Roles: admin, owner.
- `POST /jobs/{job_id}/cancel`: cancel pending, retry-pending, failed, or dead-letter jobs. Roles: admin, owner.
- `GET /jobs/{job_id}/audit-history`: list publishing-specific audit events for the job.
- `GET /settings`: read workspace publishing settings.
- `PUT /settings`: update owner-only workspace publishing settings, including retry policy, queue concurrency, timezone, and deterministic mock provider behavior.

Queue jobs pin `draft_version_id` and use a workspace-scoped idempotency key to prevent duplicate publishing records.

Processing uses the deterministic mock provider only. It never calls LinkedIn, X, Instagram, Facebook, OAuth, browser automation, or external APIs.

Mock behavior can be set per workspace with `mock_provider_behavior`: `deterministic`, `success`, `transient_failure`, or `permanent_failure`. In deterministic mode, draft content containing `[mock:transient]` creates a retryable failure and `[mock:permanent]` creates a dead-letter failure; all other drafts publish successfully.

## Error Semantics

- `401`: missing or invalid authentication.
- `403`: workspace access denied or insufficient role.
- `404`: resource not found in the active workspace.
- `409`: lifecycle conflict, optimistic revision conflict, schedule conflict, or invalid retry/cancel transition.
- `422`: request validation error.
