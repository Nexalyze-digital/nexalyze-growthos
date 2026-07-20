# Publishing Frontend QA

Package 2 adds the responsive Publishing Engine frontend on top of the Package 1 backend APIs.

## Covered Workflows

- Draft creation.
- Draft editing and version history.
- Content Studio save-to-draft handoff.
- Content Library search, filters, pagination, archive, restore, duplicate, and submit actions.
- Draft detail and platform preview.
- Review queue with approve, reject, request revision, and comment entry.
- Calendar foundation with month, week, day modes and scheduling form.
- Queue view with retry, cancel, and attempt display.
- Publishing settings and social connection status readouts.
- Viewer, editor, admin, and owner role-aware controls.
- Mobile navigation to Publishing.

## Validation Commands

Backend:

```powershell
cd apps\api
.\.venv\Scripts\python.exe -m pytest tests
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

## Accessibility Review

- Publishing tabs use `role="tablist"` and `role="tab"`.
- Forms use visible labels.
- Icon-only actions have `aria-label` and `title`.
- Status and error messages are text-based.
- Viewer controls are hidden in the UI while backend authorization remains authoritative.
- Mobile navigation includes the Publishing target.

## Current Package Limits

- Settings are displayed from current backend defaults because Package 1 does not expose settings mutation endpoints.
- Social connection status is mock/not-connected only.
- Real external publishing providers, OAuth, queue processing workers, and provider adapters are outside Package 2.
