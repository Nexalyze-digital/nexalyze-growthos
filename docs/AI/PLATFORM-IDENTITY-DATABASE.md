# Platform Identity And Database Foundation

Status: v0.5.0 release candidate

GrowthOS v0.5.0 converts the app from local single-user JSON-only workflows into a multi-user platform foundation with authentication, organizations, workspaces, roles, audit events, and database-backed Brand Brain and Research Hub persistence.

## Authentication

- User registration.
- Login.
- Logout.
- JWT-style HMAC access tokens.
- Refresh token rotation and revocation.
- Password hashing with PBKDF2-HMAC-SHA256.
- Current-user endpoint.
- Account activation status.
- Frontend login and registration gate.
- Session persistence in browser local storage.

## Authorization

Workspace memberships support:

- `owner`
- `admin`
- `editor`
- `viewer`

Write actions require owner, admin, or editor access. Viewer users can read workspace resources but cannot create, update, regenerate, or delete protected resources.

## Workspace Scope

The frontend sends:

- `Authorization: Bearer <access-token>`
- `X-Workspace-Id: <workspace-id>`

The backend verifies token validity, account activation, workspace membership, and role permissions before serving Brand Brain, Research Hub, or AI Content Studio operations.

## Database

The default local database URL is:

```powershell
DATABASE_URL=sqlite:///data/growthos.db
```

Production should use PostgreSQL after environment-specific validation:

```powershell
DATABASE_URL=postgresql+psycopg://user:password@host:5432/growthos
```

PostgreSQL driver installation, production secret management, migration rehearsal, backup/restore rehearsal, and connection-pool validation are deployment concerns and should not commit credentials.

## PostgreSQL Validation Checklist

- Install the production PostgreSQL driver in the deployment environment.
- Set `APP_ENV=production`.
- Set a strong `JWT_SECRET_KEY` outside source control.
- Set `DATABASE_URL` to the target PostgreSQL database.
- Run `alembic upgrade head` against a fresh PostgreSQL database.
- Run the backend test suite against a disposable PostgreSQL database.
- Rehearse JSON migration dry-run and live migration on a backup copy.
- Confirm rollback using database backup/restore procedures.
- Confirm API startup does not rely on SQLite-only behavior.

## Migration

JSON migration utility:

```powershell
cd apps\api
.\.venv\Scripts\python.exe scripts\migrate_json_to_db.py --workspace-id <workspace-id> --dry-run
.\.venv\Scripts\python.exe scripts\migrate_json_to_db.py --workspace-id <workspace-id>
```

The live migration creates `.bak` files beside migrated JSON stores and writes Brand Brain and Research Hub payloads transactionally into the database.

## Security Notes

- No secrets are committed.
- Development JWT secret must be replaced outside local development.
- CORS is scoped to configured origins and the headers GrowthOS uses.
- Authentication endpoints include basic in-memory rate limiting.
- Audit events are recorded for login, logout, registration, workspace creation, and data changes.

## Limitations

- No MFA.
- No password reset.
- No email verification.
- No production PostgreSQL connection is committed.
- No advanced session device management.
- No admin portal yet.
