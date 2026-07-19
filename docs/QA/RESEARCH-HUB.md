# Research Hub QA

Status: v0.4.0 validation guide

## Automated Validation

Backend:

```powershell
cd apps/api
.\.venv\Scripts\python.exe -m pytest tests
```

Frontend:

```powershell
cd apps/web
npm run lint
npm run build
```

## Backend Coverage

- Successful research run.
- Validation failures.
- Brand Brain injection.
- Ollama success with mocked HTTP response.
- Ollama timeout fallback.
- Ollama connection fallback.
- Malformed Ollama JSON fallback.
- Mock fallback.
- Save and list runs.
- Retrieve one run.
- Regenerate.
- Delete.
- Corrupted JSON storage.
- Research integrity rules.
- Source URL preservation only when supplied by the user.

## Browser Smoke Coverage

Validate:

- AI Content Studio still works.
- Brand Brain still saves and applies context.
- Research request runs.
- Results render.
- Copy report works.
- Regenerate works.
- Delete works.
- Research history works.
- Mobile navigation works.
- Provider badge renders.
- Mock fallback notice renders when local AI is unavailable.
- API offline state renders when the backend is stopped.
- No browser console errors during connected flows.

## Manual Notes

Research Hub v0.4.0 does not browse the live web. All outputs must be treated as AI-generated synthesis unless a user supplied source URL is shown in source notes.
