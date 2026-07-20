# Publishing Security Review

## Trust Boundaries

- Frontend role-aware controls are not trusted.
- Backend request context and role checks are authoritative.
- Draft content and provider output are untrusted text.
- Future social API credentials are secrets and out of scope for v0.6.0.
- Mock adapter must not make network calls.

## Key Risks

| Risk | Mitigation |
| --- | --- |
| Unauthorized publishing | Admin/owner checks on schedule, enqueue, retry, cancel, approve, reject. |
| Viewer write access | Hide write controls and enforce backend `403`. |
| Editor self-approval | Workspace setting `prevent_self_approval`; service rejects matching submitter/reviewer. |
| Posting wrong version | Queue job pins draft version id/version number. |
| Duplicate publish | Idempotency key unique per workspace. |
| Stored XSS | Render draft text as text only; no raw HTML. |
| Credential leakage | No real tokens stored in v0.6.0; future connections need encrypted secret storage. |
| Provider error leakage | Store non-sensitive response summaries only. |
| Schedule time mistakes | Store UTC and workspace timezone; validate past times and conflicts. |

## Role Enforcement

- Viewer: read-only.
- Editor: draft create/edit/duplicate/archive/submit.
- Admin: editor plus approve/reject/schedule/retry/cancel.
- Owner: admin plus publishing settings.

## External Adapter Policy

- Use official platform APIs only.
- Do not use browser automation to post to social platforms.
- Do not add paid APIs without approval.
- Do not request OAuth scopes until official credentials are available.

## Platform Debt Outside v0.6.0

- localStorage tokens.
- In-memory rate limiting.
- Hosted PostgreSQL validation.
- MFA.
- Email verification.
- Password reset.
- Invite flow.
- Admin portal.
- PostCSS advisory.
- CI observation period.
