# Platform Identity And Database QA

Status: v0.5.0 release candidate

## Automated Validation

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

## Backend Coverage

- Registration.
- Login.
- Logout.
- Current user.
- Refresh-token rotation and reuse rejection.
- Password validation.
- Workspace creation.
- Workspace isolation for Brand Brain.
- Viewer write denial.
- JSON migration dry run.
- JSON migration live local test.
- AI Content Studio regression.
- Brand Brain regression.
- Research Hub regression.

## Browser Smoke Coverage

The Research Hub smoke script now includes authentication:

```powershell
node apps\web\tests\research-hub-smoke.mjs
```

Validated flows:

- Registration gate.
- Protected dashboard access.
- Workspace-scoped Research Hub run.
- Copy.
- Regenerate.
- Delete.
- History.
- Mobile navigation.
- AI Content Studio regression.
- Mock provider.
- Mock fallback provider.
- Live Ollama provider where available.

## Manual Checks

- Register a new account.
- Confirm the workspace switcher appears.
- Create a Brand Brain profile.
- Create a Research Hub run.
- Generate content from AI Content Studio.
- Confirm logout returns to the authentication screen.
- Confirm an inactive or invalid token cannot access protected routes.

## Known Test Limitations

- Playwright smoke is still run as a local script rather than CI.
- SQLite is used for automated tests; production PostgreSQL validation requires environment-specific credentials and must be completed before customer-data deployment.
