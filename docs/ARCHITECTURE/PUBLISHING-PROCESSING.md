# Publishing Processing Architecture

Package 3 introduces the backend processing engine for Publishing. It is intentionally local and deterministic: no live social APIs, OAuth flows, browser automation, or provider credentials are used.

## Responsibilities

- Process workspace-scoped publishing jobs from `pending` and `retry_pending` states.
- Record durable provider attempts.
- Apply deterministic mock provider outcomes for LinkedIn, X, Instagram, and Facebook.
- Schedule transient retries with exponential backoff.
- Move permanent failures and exhausted retries to `dead_letter`.
- Prevent duplicate publishing records with workspace-scoped idempotency keys.
- Capture publishing audit history for created, queued, processing, retry, published, failed, dead-letter, and cancelled actions.

## Data Model

- `publishing_jobs`: durable queue job with draft version pinning, status, retry count, retry window, idempotency key, and provider summary.
- `publishing_attempts`: immutable attempt history with attempt number, status, provider post id, error category, summary, and published timestamp.
- `publishing_audit_events`: publishing-specific audit trail with workspace, actor, draft, draft version, provider, action, attempt number, and timestamp.
- `workspace_publishing_settings`: retry policy, default timezone, queue concurrency, approval behavior, and deterministic mock provider behavior.

## Processing States

- `pending`: queued and ready.
- `processing`: locked by the processor.
- `published`: mock provider accepted the post.
- `retry_pending`: retryable failure waiting for a retry window.
- `failed`: attempt-level failure state.
- `dead_letter`: permanent failure or retry budget exhausted.
- `cancelled`: stopped by an admin or owner.

## Provider Behavior

The mock provider supports `deterministic`, `success`, `transient_failure`, and `permanent_failure` modes. In deterministic mode, `[mock:transient]` in draft content produces a retryable error and `[mock:permanent]` produces a permanent rejection. All other content succeeds.

## Security

Processing requires owner or admin role. All repository reads are workspace-scoped, and cross-workspace job access returns not found. Settings updates require owner role. Error messages avoid provider secrets because no social credentials exist in this package.

## Package Boundary

Package 3 proves queue mechanics and release safety. Live provider adapters, OAuth tokens, credential storage, webhook handling, and real social API publishing belong to a future package.
