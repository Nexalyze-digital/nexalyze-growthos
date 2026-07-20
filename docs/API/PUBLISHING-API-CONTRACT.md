# Publishing API Contract

Base path: `/api/v1/publishing`

All endpoints require authentication. All write endpoints require backend role enforcement.

## Drafts

### `POST /drafts`

Create a draft.

Required role: editor, admin, owner.

Request fields:

- `title`
- `body`
- `platform`
- `hashtags`
- `brand_id`
- `source_research_run_id`

Response: draft detail with latest version.

### `GET /drafts`

List drafts with filters.

Query:

- `search`
- `platform`
- `status`
- `brand_id`
- `author_id`
- `date_from`
- `date_to`
- `archived`
- `page`
- `page_size`
- `sort`

Response: paginated draft summaries.

### `GET /drafts/{draft_id}`

Get draft detail.

### `PUT /drafts/{draft_id}`

Update draft and create a draft version.

Required role: editor, admin, owner.

### `POST /drafts/{draft_id}/duplicate`

Duplicate a draft into `generated` or `edited` state.

Required role: editor, admin, owner.

### `POST /drafts/{draft_id}/archive`

Archive a draft.

Required role: editor, admin, owner.

### `POST /drafts/{draft_id}/restore`

Restore an archived draft.

Required role: editor, admin, owner.

### `DELETE /drafts/{draft_id}`

Soft delete a draft.

Required role: admin, owner for other users' drafts; editor only for own draft before approval.

### `GET /drafts/{draft_id}/versions`

List version history.

## Review

### `POST /drafts/{draft_id}/submit`

Submit for review.

Required role: editor, admin, owner.

### `POST /drafts/{draft_id}/approve`

Approve a draft.

Required role: admin, owner.

Policy: reject self-approval when workspace setting requires it.

### `POST /drafts/{draft_id}/reject`

Reject a draft with reviewer comment.

Required role: admin, owner.

### `POST /drafts/{draft_id}/request-revision`

Request revision with comment.

Required role: admin, owner.

### `POST /approvals/{approval_id}/comments`

Add approval comment.

Required role: editor, admin, owner, scoped by workflow participation.

### `GET /drafts/{draft_id}/review-history`

Return approvals and comments.

## Scheduling

### `POST /drafts/{draft_id}/schedule`

Schedule approved draft.

Required role: admin, owner.

### `PUT /schedules/{schedule_id}`

Reschedule.

Required role: admin, owner.

### `POST /schedules/{schedule_id}/unschedule`

Unschedule.

Required role: admin, owner.

### `GET /calendar`

Query calendar events.

Query:

- `view`: month, week, day.
- `start`
- `end`
- `platform`
- `brand_id`
- `status`

## Publishing

### `POST /drafts/{draft_id}/enqueue`

Create or reuse queue job for approved draft.

Required role: admin, owner.

### `POST /jobs/{job_id}/retry`

Retry failed transient job.

Required role: admin, owner.

### `POST /jobs/{job_id}/cancel`

Cancel pending job.

Required role: admin, owner.

### `GET /jobs`

List queue jobs.

### `GET /jobs/{job_id}`

Get job detail and attempts.

### `GET /drafts/{draft_id}/publishing-history`

Get publishing history for draft.

## Connections

### `GET /connections`

List social connection status.

### `GET /connections/{platform}`

Get platform connection status and future OAuth boundary metadata.

No OAuth start/callback endpoint is in v0.6.0 unless official credentials are available.

## Error Semantics

- `401`: missing or invalid authentication.
- `403`: role or workspace authorization denied.
- `404`: not found in active workspace.
- `409`: invalid lifecycle transition, conflict, duplicate idempotency collision, schedule conflict.
- `422`: validation error.
