# Publishing Data Model

## Tables

### drafts

- `id` string UUID primary key.
- `workspace_id` foreign key to `workspaces.id`, indexed.
- `brand_id` nullable foreign key to `brand_brains.id`, indexed.
- `source_research_run_id` nullable foreign key to `research_runs.id`.
- `platform` string, indexed.
- `title` string.
- `body` text.
- `hashtags` text JSON array.
- `status` string, indexed.
- `created_by_user_id` foreign key to `users.id`.
- `updated_by_user_id` foreign key to `users.id`.
- `archived_at` nullable timestamp, indexed.
- `deleted_at` nullable timestamp, indexed.
- `created_at` timestamp.
- `updated_at` timestamp.

Indexes:

- `(workspace_id, status, updated_at)`.
- `(workspace_id, platform, status)`.
- `(workspace_id, brand_id)`.
- `(workspace_id, archived_at)`.
- Full-text search can be deferred; v0.6.0 can use filtered `ILIKE` for local scale.

### draft_versions

- `id` string UUID primary key.
- `draft_id` foreign key to `drafts.id`, indexed.
- `version_number` integer.
- `title` string.
- `body` text.
- `hashtags` text JSON array.
- `created_by_user_id` foreign key to `users.id`.
- `created_at` timestamp.

Unique constraint:

- `(draft_id, version_number)`.

### approvals

- `id` string UUID primary key.
- `draft_id` foreign key to `drafts.id`, indexed.
- `submitted_by_user_id` foreign key to `users.id`.
- `reviewed_by_user_id` nullable foreign key to `users.id`.
- `status` string: pending, approved, rejected, revision_requested.
- `submitted_at` timestamp.
- `reviewed_at` nullable timestamp.

### approval_comments

- `id` string UUID primary key.
- `approval_id` foreign key to `approvals.id`, indexed.
- `user_id` foreign key to `users.id`.
- `comment_type` string: note, rejection_reason, revision_request.
- `body` text.
- `created_at` timestamp.

### schedules

- `id` string UUID primary key.
- `draft_id` foreign key to `drafts.id`, unique when active.
- `draft_version_id` foreign key to `draft_versions.id`.
- `workspace_id` foreign key to `workspaces.id`, indexed.
- `platform` string, indexed.
- `scheduled_at_utc` timestamp, indexed.
- `workspace_timezone` string.
- `status` string: scheduled, unscheduled, publishing, published, failed.
- `created_by_user_id` foreign key to `users.id`.
- `updated_by_user_id` foreign key to `users.id`.
- `created_at` timestamp.
- `updated_at` timestamp.

Indexes:

- `(workspace_id, scheduled_at_utc)`.
- `(workspace_id, platform, scheduled_at_utc)`.

### publishing_jobs

- `id` string UUID primary key.
- `workspace_id` foreign key to `workspaces.id`, indexed.
- `draft_id` foreign key to `drafts.id`, indexed.
- `draft_version_id` foreign key to `draft_versions.id`.
- `schedule_id` nullable foreign key to `schedules.id`.
- `platform` string.
- `status` string: pending, processing, succeeded, failed, cancelled.
- `retry_count` integer.
- `next_retry_at` nullable timestamp.
- `idempotency_key` string.
- `error_category` nullable string.
- `provider_response_summary` nullable text.
- `created_at` timestamp.
- `updated_at` timestamp.

Unique constraint:

- `(workspace_id, idempotency_key)`.

### publishing_attempts

- `id` string UUID primary key.
- `job_id` foreign key to `publishing_jobs.id`, indexed.
- `attempt_number` integer.
- `status` string.
- `provider_post_id` nullable string.
- `error_category` nullable string.
- `provider_response_summary` nullable text.
- `published_at` nullable timestamp.
- `created_at` timestamp.

Unique constraint:

- `(job_id, attempt_number)`.

### social_connections

- `id` string UUID primary key.
- `workspace_id` foreign key to `workspaces.id`, indexed.
- `platform` string.
- `status` string: not_connected, connected, expired, error.
- `display_name` nullable string.
- `scopes_summary` nullable string.
- `last_checked_at` nullable timestamp.
- `created_at` timestamp.
- `updated_at` timestamp.

Unique constraint:

- `(workspace_id, platform)`.

No tokens are stored in v0.6.0.

### workspace_publishing_settings

- `id` string UUID primary key.
- `workspace_id` unique foreign key to `workspaces.id`.
- `timezone` string default `UTC`.
- `approval_required` boolean default true.
- `prevent_self_approval` boolean default true.
- `default_platforms` text JSON array.
- `created_at` timestamp.
- `updated_at` timestamp.

## Soft Delete Strategy

- Use `archived_at` for user-visible archive.
- Use `deleted_at` only for admin/internal cleanup where appropriate.
- Default list APIs exclude `deleted_at`.
- Archive is reversible and is the primary user-facing removal flow in v0.6.0.
- Soft delete is not a permanent delete and should not remove audit, approval, schedule, or publishing history.

## Migration Strategy

- Add all publishing tables in one Alembic revision if implementation is one PR.
- Prefer separate migration PR if implementation is split.
- Validate SQLite and PostgreSQL.
- Downgrade drops tables in reverse dependency order.

## Rollback Strategy

- Before release candidate, downgrade can drop publishing tables.
- After real data exists, rollback should restore a database backup instead of destructive downgrade.
