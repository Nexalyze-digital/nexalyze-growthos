$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$webDir = Join-Path $repoRoot "apps/web"
$nodeModules = Join-Path $webDir "node_modules"

if (-not (Test-Path -LiteralPath $nodeModules)) {
  Write-Error "Missing frontend dependencies at apps/web/node_modules. Run npm install from apps/web first."
}

Set-Location -LiteralPath $webDir
npm run dev
