# AI Content Studio QA

## Prerequisites

- Python virtual environment exists at `apps/api/.venv`.
- Frontend dependencies exist at `apps/web/node_modules`.
- Backend uses the mock provider; no AI service key is required.
- Ollama is optional. If enabled and unavailable, the API should fall back to the mock provider.

## Backend Startup Command

```powershell
.\scripts\run-api.ps1
```

Expected backend URL: `http://localhost:8000`

## Frontend Startup Command

```powershell
.\scripts\run-web.ps1
```

Expected frontend URL: `http://localhost:3000`

## Test Scenarios

- Open `http://localhost:3000` and confirm the GrowthOS shell loads.
- Enter `AI automation for small businesses`.
- Select each platform once: LinkedIn, X, Instagram, Facebook.
- Select audience, goal, and tone values.
- Add optional instructions and generate content.

## Expected Results

- Generate remains disabled until the topic has at least 3 characters.
- Successful generation displays title, body, hashtags, platform, and tone.
- Successful generation displays a provider badge: Ollama, Mock fallback, or Mock.
- LinkedIn output is multi-paragraph and business-oriented.
- X output is concise.
- Instagram output reads like a visual caption.
- Facebook output is conversational and community-friendly.
- Summary metrics are labeled as demonstration data.

## Mobile Validation

- Resize below tablet width and confirm sidebar becomes bottom navigation.
- Form fields stack vertically.
- Output actions remain tappable and do not overlap content.

## API-Offline Validation

- Stop the backend.
- Submit a valid form.
- Confirm the UI shows a clear API-offline error and retry action.

## Ollama Fallback Validation

- Set `AI_PROVIDER=ollama`.
- Stop Ollama or use an unreachable `OLLAMA_BASE_URL`.
- Start the backend and frontend.
- Generate a valid post.
- Confirm content is returned with a Mock fallback provider badge.
- Confirm the non-blocking fallback message appears.

## Copy Validation

- Generate a post.
- Click Copy full post.
- Confirm the temporary Copied state appears.
- Paste into a text editor and confirm title, body, and hashtags are included.

## Regeneration Validation

- Generate a post.
- Change tone or platform.
- Click Regenerate.
- Confirm the request uses the current form values and updates the output.
