# PostgreSQL Validation

## Summary

GrowthOS v0.5.1 validates the v0.5.0 identity, workspace, authorization, Brand Brain, Research Hub, and migration foundation against a real local PostgreSQL instance.

Validated local server:

- PostgreSQL: 17.10
- Validation database: `growthos_v051_validation`
- Restore rehearsal database: `growthos_v051_restore`
- Connection URL pattern: `postgresql+psycopg://postgres@localhost:5432/<database>`

No real production credentials are committed or required by this document.

## Validation Scope

- Database creation.
- SQLAlchemy connection through `psycopg`.
- Alembic upgrade from empty database.
- Alembic downgrade to base.
- Alembic re-upgrade to head.
- User registration and login.
- Refresh-token rotation and reuse rejection.
- Workspace creation.
- Role and permission enforcement.
- Workspace-scoped Brand Brain persistence.
- Workspace-scoped Research Hub persistence.
- JSON-to-PostgreSQL migration.
- Duplicate migration protection.
- Transaction rollback coverage.
- Backup and restore rehearsal.

## Commands

Create disposable validation database:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "DROP DATABASE IF EXISTS growthos_v051_validation WITH (FORCE);"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE growthos_v051_validation;"
```

Run migration validation:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres@localhost:5432/growthos_v051_validation"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe downgrade base
.\.venv\Scripts\alembic.exe upgrade head
```

Run backend tests against PostgreSQL:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres@localhost:5432/growthos_v051_validation"
$env:JWT_SECRET_KEY="test-secret-key-for-postgresql-validation"
.\.venv\Scripts\python.exe -m pytest tests
```

## Result

- PostgreSQL connection: passed.
- Alembic upgrade/downgrade/re-upgrade: passed.
- Backend suite on PostgreSQL: passed.
- Backup/restore rehearsal: passed.
- JSON migration and duplicate protection: passed through PostgreSQL-backed backend tests.

## Notes

SQLite remains supported for local default development. PostgreSQL should be used for production-oriented validation and deployment rehearsal.
