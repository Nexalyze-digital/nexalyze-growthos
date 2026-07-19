# Token Storage Review

## Current Approach

GrowthOS stores access and refresh tokens in browser `localStorage` under `growthos.session.v1`. This supports local development and simple session restoration without a cookie backend.

## Current Risk

- `localStorage` is readable by JavaScript running on the page.
- A successful XSS vulnerability could expose access and refresh tokens.
- Refresh tokens in browser storage increase impact compared with short-lived access tokens only.
- There is no CSRF exposure from bearer tokens in `localStorage` by default, but that changes if GrowthOS migrates to cookies.

## v0.5.1 Improvements

- Automatic access-token refresh before expired authenticated requests.
- One retry after a 401 response.
- Shared refresh promise to prevent duplicate simultaneous refresh calls.
- Session clearing when refresh fails.
- Workspace selection preservation after successful refresh.
- Viewer write controls hidden in the frontend while backend authorization remains authoritative.

## HttpOnly Cookie Migration Recommendation

Future production releases should move refresh-token storage to secure, HttpOnly, SameSite cookies and keep access tokens short lived.

Migration path:

1. Add backend cookie issuance for refresh tokens.
2. Keep bearer access tokens short lived.
3. Add CSRF protection for cookie-authenticated unsafe methods.
4. Support a compatibility window for existing localStorage sessions.
5. Clear legacy localStorage refresh tokens after successful cookie migration.
6. Add Playwright coverage for refresh, logout, CSRF rejection, and expired-session behavior.

## CSRF Considerations

Current bearer-token requests are not automatically attached by the browser, limiting classic CSRF risk. Cookie-based refresh will require SameSite settings and CSRF tokens for unsafe operations.

## XSS Considerations

The current UI renders React text content and does not intentionally inject raw HTML. Future rich-text, publishing previews, or external-source rendering must be reviewed carefully before production token hardening can be considered complete.
