# Publishing Processing QA

Package 3 validates the deterministic mock Publishing Processing Engine.

## Backend Coverage

- Queue processing success to `published`.
- Provider post ID and published timestamp capture.
- Transient failure to `retry_pending`.
- Manual retry with retry budget enforcement.
- Permanent failure to `dead_letter`.
- Retry-window validation.
- Owner-only processing settings.
- Viewer denial for process, retry, and cancel.
- Workspace isolation for job and audit history reads.
- Publishing audit history ordering.
- Existing Publishing backend foundation regression.

## Frontend Coverage

- Queue displays new statuses.
- Admins can process the next due job from the queue view.
- Per-job process, retry, and cancel controls remain keyboard-accessible icon buttons.
- Attempt summaries remain visible in queue details.
- Mobile layout keeps queue controls stacked and readable.

## Validation Commands

Backend:

```powershell
cd apps\api
.\.venv\Scripts\python.exe -m pytest
```

Frontend:

```powershell
cd apps\web
npm run lint
npm run build
```

Browser smoke:

```powershell
cd apps\web
node tests\publishing-smoke.mjs
```

## Source And Provider Integrity

The package performs deterministic mock publishing only. It does not claim that any post was sent to a live LinkedIn, X, Instagram, or Facebook account. Mock provider post IDs are local identifiers for validation.
