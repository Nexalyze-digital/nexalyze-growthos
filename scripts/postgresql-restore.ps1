param(
  [Parameter(Mandatory = $true)]
  [string]$DatabaseUrl,

  [Parameter(Mandatory = $true)]
  [string]$InputPath,

  [string]$PgRestorePath = "C:\Program Files\PostgreSQL\17\bin\pg_restore.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $PgRestorePath)) {
  throw "pg_restore was not found at $PgRestorePath. Pass -PgRestorePath with the installed PostgreSQL path."
}

if (-not (Test-Path -LiteralPath $InputPath)) {
  throw "Backup file was not found at $InputPath."
}

& $PgRestorePath --clean --if-exists --no-owner --dbname=$DatabaseUrl $InputPath
if ($LASTEXITCODE -ne 0) {
  throw "PostgreSQL restore failed with exit code $LASTEXITCODE."
}

"PostgreSQL restore completed."
