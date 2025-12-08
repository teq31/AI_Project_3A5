Write-Host "Starting SmarTest Backend Server..." -ForegroundColor Green
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -m venv .venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Yellow
py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

Write-Host "Starting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Green
py -m uvicorn app.main:app --reload --port 8000

