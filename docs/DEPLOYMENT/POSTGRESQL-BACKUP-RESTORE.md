# PostgreSQL Backup And Restore

## Purpose

This document defines the v0.5.1 backup and restore rehearsal for GrowthOS PostgreSQL databases. Use it with disposable test databases first. Do not run destructive restore commands against production without a verified backup and approval.

## Prerequisites

- PostgreSQL server installed and running.
- `pg_dump` and `pg_restore` available or passed explicitly to the helper scripts.
- A test database URL with sufficient privileges.
- No real credentials committed to source control.

## Backup

```powershell
$backup = Join-Path $env:TEMP "growthos-v051-validation.dump"
.\scripts\postgresql-backup.ps1 `
  -DatabaseUrl "postgresql://postgres@localhost:5432/growthos_v051_validation" `
  -OutputPath $backup
```

The script uses custom-format `pg_dump` and returns the generated file path and size.

## Restore

Create a disposable restore target:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "DROP DATABASE IF EXISTS growthos_v051_restore WITH (FORCE);"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE growthos_v051_restore;"
```

Restore into the disposable database:

```powershell
.\scripts\postgresql-restore.ps1 `
  -DatabaseUrl "postgresql://postgres@localhost:5432/growthos_v051_restore" `
  -InputPath $backup
```

Verify restored data:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5432 -U postgres -d growthos_v051_restore -c "select count(*) from users;"
```

## Rollback Steps

1. Stop application writes.
2. Confirm the backup file is present and readable.
3. Restore into a separate database first.
4. Run smoke validation against the restored database.
5. Promote the restored database only after validation passes.
6. Preserve failed migration inputs and logs for diagnosis.

## Rehearsal Result

v0.5.1 backup and restore rehearsal passed using `growthos_v051_validation` and `growthos_v051_restore`.
