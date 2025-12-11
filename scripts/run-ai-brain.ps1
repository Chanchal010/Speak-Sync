# Run AI Brain Service
# Quick start script for the AI Brain Service

Write-Host "`n🧠 Starting AI Brain Service..." -ForegroundColor Cyan

# Navigate to service directory
Set-Location "apps\ai-brain-service"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run .\scripts\setup-python-services.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Run .\scripts\setup-env.ps1 first" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor White
& ".\venv\Scripts\Activate.ps1"

# Start the service
Write-Host "✅ Starting AI Brain Service on port 8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

uvicorn src.main:app --reload --port 8000
