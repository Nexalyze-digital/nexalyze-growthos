# Publishing User Flows

## Content Library

- Search drafts by title/body.
- Filter by platform, status, brand, author, date, and archived state.
- Sort by updated date, scheduled date, status, platform.
- Show empty, loading, and error states.
- Paginate deterministically.
- Viewer sees read-only rows.

## Draft Detail

- Show title, body, hashtags, platform, brand, author, status, latest version, review status, schedule status, and publishing history.
- Show audit-friendly timestamps.
- Provide duplicate/archive/restore actions only to roles allowed by backend policy.

## Draft Editor

- Edit title, body, hashtags, platform, and brand.
- Save creates a new version.
- Validate platform constraints before save.
- Include unsaved-change warning if implemented safely.

## Review Queue

- Editors submit for review.
- Admin/owner approve, reject, or request revision.
- Reviewer comments are visible in history.
- Self-approval prevention should surface a calm `403`/policy message.

## Publishing Calendar

- Month, week, and day views.
- Filters by platform, brand, status.
- Timezone visible in header.
- Schedule approved drafts only.
- Reschedule and unschedule actions for admin/owner.

## Publishing Queue

- Show pending, processing, succeeded, failed, cancelled jobs.
- Show retry count, next retry time, error category, and safe provider summary.
- Admin/owner retry transient failures or cancel pending jobs.

## Publishing Settings

- Owner can set workspace timezone.
- Owner can enable/disable approval requirement.
- Owner can enable/disable self-approval prevention.
- Owner can choose default platforms.

## Social Connection Status

- v0.6.0 shows mock/not-connected statuses only.
- Real OAuth connection flows are future work.

## Accessibility Requirements

- Native buttons/selects/inputs where possible.
- Visible labels for every form field.
- Keyboard reachable table and calendar controls.
- Focus stays predictable after modal/dialog actions.
- Status messages are text, not color-only.
- Mobile layout preserves readable cards/tables without horizontal traps.
