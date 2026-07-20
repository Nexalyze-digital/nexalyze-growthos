# Publishing Engine Architecture

## Package Scope

Package 1 implements the Publishing Engine backend foundation. Package 2 adds frontend workflows on top of those APIs. Package 3 adds deterministic mock queue processing. These packages do not add real OAuth, live social publishing, external provider adapters, or browser automation.

## Backend Layers

- Routes: `app/api/routes/publishing.py`
- Schemas: `app/schemas/publishing.py`
- Repositories:
  - `app/repositories/draft_repository.py`
  - `app/repositories/approval_repository.py`
  - `app/repositories/schedule_repository.py`
  - `app/repositories/publishing_repository.py`
- Services:
  - `app/services/draft_service.py`
  - `app/services/approval_service.py`
  - `app/services/schedule_service.py`
  - `app/services/publishing_queue_service.py`
- Provider: `app/providers/publishing.py`
- Persistence: SQLAlchemy models in `app/db/models.py` and Alembic revisions `20260720_0002` and `20260720_0003`.

## Frontend Layers

- Workspace: `apps/web/src/components/publishing/PublishingEngine.tsx`
- Types: `apps/web/src/types/publishing.ts`
- API client: Publishing helpers in `apps/web/src/lib/api.ts`
- Navigation: existing sidebar and mobile navigation link to `#publishing-title`

## Data Flow

1. Authenticated callers use `/api/v1/publishing/*` with an active workspace.
2. Request context validates user and workspace membership.
3. Services enforce role permissions and lifecycle transitions.
4. Repositories perform workspace-scoped persistence.
5. Queue processing writes attempts, publishing-specific audit events, and general audit events.

## Integration Points

- Authentication supplies user, workspace, and role context.
- Brand Brain can be associated through `brand_id` when the brand belongs to the same workspace.
- Research Hub can be associated through `source_research_run_id` when the research run belongs to the same workspace.
- Content Studio can hand generated output to `POST /drafts`; frontend handoff belongs to a later package.
- Content Studio can hand generated output to `POST /drafts` through the `Save draft` action.

## Safety Controls

- Workspace isolation on all reads and writes.
- Viewer read-only behavior.
- Editor draft creation/editing without approval or publishing authority.
- Admin/owner review, scheduling, queue retry, and cancel authority.
- Optimistic draft revision checks.
- Version-pinned schedules and queue jobs.
- Idempotent queue creation.
- No social tokens stored in this package.
- No external network publishing performed in this package.
- Deterministic mock processing only.
- Retry windows are enforced before processing retry-pending jobs.
- Dead-letter state prevents endless retries after permanent failures or retry exhaustion.
