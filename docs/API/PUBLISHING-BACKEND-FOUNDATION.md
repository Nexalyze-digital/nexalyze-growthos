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
- `POST /jobs/{job_id}/retry`: retry transient failed jobs. Roles: admin, owner.
- `POST /jobs/{job_id}/cancel`: cancel pending or failed jobs. Roles: admin, owner.

Queue jobs pin `draft_version_id` and use a workspace-scoped idempotency key to prevent duplicate publishing records.

## Error Semantics

- `401`: missing or invalid authentication.
- `403`: workspace access denied or insufficient role.
- `404`: resource not found in the active workspace.
- `409`: lifecycle conflict, optimistic revision conflict, schedule conflict, or invalid retry/cancel transition.
- `422`: request validation error.
