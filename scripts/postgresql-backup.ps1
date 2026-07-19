param(
  [Parameter(Mandatory = $true)]
  [string]$DatabaseUrl,

  [Parameter(Mandatory = $true)]
  [string]$OutputPath,

  [string]$PgDumpPath = "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $PgDumpPath)) {
  throw "pg_dump was not found at $PgDumpPath. Pass -PgDumpPath with the installed PostgreSQL path."
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory) {
  New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}

& $PgDumpPath --format=custom --file=$OutputPath $DatabaseUrl
if ($LASTEXITCODE -ne 0) {
  throw "PostgreSQL backup failed with exit code $LASTEXITCODE."
}

Get-Item -LiteralPath $OutputPath | Select-Object FullName, Length
