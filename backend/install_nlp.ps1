Write-Host "Installing NLP dependencies..." -ForegroundColor Green
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) {
    Write-Host "Virtual environment not found. Please run start_server.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host "Installing NLP libraries..." -ForegroundColor Yellow
py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ NLP dependencies installed successfully!" -ForegroundColor Green
    Write-Host "The system will now use semantic similarity for better answer understanding." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Some dependencies failed to install. The system will use fallback methods." -ForegroundColor Yellow
}

