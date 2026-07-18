$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "apps/api"
$venvActivate = Join-Path $apiDir ".venv/Scripts/Activate.ps1"

if (-not (Test-Path -LiteralPath $venvActivate)) {
  Write-Error "Missing API virtual environment at apps/api/.venv. Create it and install apps/api/requirements.txt first."
}

Set-Location -LiteralPath $apiDir
. $venvActivate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
