# Setup Python Services for Speak-Sync
# This script creates virtual environments and installs dependencies

Write-Host "`n🐍 Setting up Python Services" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "✅ Using $pythonVersion" -ForegroundColor Green

# Function to setup a Python service
function Setup-PythonService {
    param(
        [string]$ServicePath,
        [string]$ServiceName
    )
    
    Write-Host "`n📦 Setting up $ServiceName..." -ForegroundColor Cyan
    Write-Host "-" * 50 -ForegroundColor Gray
    
    # Navigate to service directory
    Push-Location $ServicePath
    
    # Check if venv already exists
    if (Test-Path "venv") {
        Write-Host "⚠️  Virtual environment already exists, skipping creation" -ForegroundColor Yellow
    }
    else {
        Write-Host "Creating virtual environment..." -ForegroundColor White
        python -m venv venv
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Virtual environment created" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            Pop-Location
            return $false
        }
    }
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor White
    & ".\venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor White
    python -m pip install --upgrade pip --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip upgraded" -ForegroundColor Green
    }
    
    # Install dependencies
    if (Test-Path "requirements.txt") {
        Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor White
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            Pop-Location
            return $false
        }
    }
    else {
        Write-Host "⚠️  requirements.txt not found" -ForegroundColor Yellow
    }
    
    # Deactivate virtual environment
    deactivate
    
    Pop-Location
    return $true
}

# Setup AI Brain Service
$aiBrainSuccess = Setup-PythonService -ServicePath "apps\ai-brain-service" -ServiceName "AI Brain Service"

# Setup Lifestyle Service
$lifestyleSuccess = Setup-PythonService -ServicePath "apps\lifestyle-service" -ServiceName "Lifestyle Service"

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "📊 Setup Summary" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

if ($aiBrainSuccess) {
    Write-Host "✅ AI Brain Service - Ready" -ForegroundColor Green
}
else {
    Write-Host "❌ AI Brain Service - Failed" -ForegroundColor Red
}

if ($lifestyleSuccess) {
    Write-Host "✅ Lifestyle Service - Ready" -ForegroundColor Green
}
else {
    Write-Host "❌ Lifestyle Service - Failed" -ForegroundColor Red
}

Write-Host "`n💡 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add your API keys to apps\ai-brain-service\.env" -ForegroundColor White
Write-Host "   - GROQ_API_KEY" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Run services using:" -ForegroundColor White
Write-Host "   .\scripts\run-ai-brain.ps1" -ForegroundColor Yellow
Write-Host "   .\scripts\run-lifestyle.ps1" -ForegroundColor Yellow
Write-Host ""
