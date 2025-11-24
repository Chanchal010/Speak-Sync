# Speak-Sync Services Health Check Script
# This script checks if all required services and dependencies are ready

Write-Host "`n🔍 Speak-Sync Services Health Check" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Function to check if a command exists
function Test-Command($command) {
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Function to check URL connectivity
function Test-ServiceUrl($url, $name) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ $name is reachable" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ $name is NOT reachable" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# Function to check if file exists
function Test-EnvFile($path, $serviceName) {
    if (Test-Path $path) {
        Write-Host "✅ $serviceName .env file exists" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "❌ $serviceName .env file missing" -ForegroundColor Red
        return $false
    }
}

# Function to check Python venv
function Test-PythonVenv($path, $serviceName) {
    $venvPath = Join-Path $path "venv"
    if (Test-Path $venvPath) {
        Write-Host "✅ $serviceName virtual environment exists" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "⚠️  $serviceName virtual environment not found" -ForegroundColor Yellow
        return $false
    }
}

Write-Host "`n📦 Checking Prerequisites..." -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray

# Check Python
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
}
else {
    Write-Host "❌ Python is NOT installed" -ForegroundColor Red
}

# Check Node.js
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "✅ Node.js installed: $nodeVersion" -ForegroundColor Green
}
else {
    Write-Host "❌ Node.js is NOT installed" -ForegroundColor Red
}

# Check pnpm
if (Test-Command "pnpm") {
    $pnpmVersion = pnpm --version
    Write-Host "✅ pnpm installed: v$pnpmVersion" -ForegroundColor Green
}
else {
    Write-Host "❌ pnpm is NOT installed" -ForegroundColor Red
}

Write-Host "`n📄 Checking Environment Files..." -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray

Test-EnvFile "apps\gateway-service\.env" "Gateway Service"
Test-EnvFile "apps\scheduler-service\.env" "Scheduler Service"
Test-EnvFile "apps\worker-service\.env" "Worker Service"
Test-EnvFile "apps\ai-brain-service\.env" "AI Brain Service"
Test-EnvFile "apps\lifestyle-service\.env" "Lifestyle Service"

Write-Host "`n🐍 Checking Python Virtual Environments..." -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray

Test-PythonVenv "apps\ai-brain-service" "AI Brain Service"
Test-PythonVenv "apps\lifestyle-service" "Lifestyle Service"

Write-Host "`n📦 Checking Node Modules..." -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray

if (Test-Path "node_modules") {
    Write-Host "✅ Root node_modules exists" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Root node_modules not found - run 'pnpm install'" -ForegroundColor Yellow
}

Write-Host "`n🌐 Checking Running Services..." -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray
Write-Host "Note: Services must be running for these checks to pass" -ForegroundColor Gray

Test-ServiceUrl "http://localhost:3000/health" "Gateway Service (3000)"
Test-ServiceUrl "http://localhost:3001/health" "Scheduler Service (3001)"
Test-ServiceUrl "http://localhost:8000/health" "AI Brain Service (8000)"
Test-ServiceUrl "http://localhost:8001/health" "Lifestyle Service (8001)"

Write-Host "`n" -NoNewline
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "✨ Health check complete!" -ForegroundColor Cyan
Write-Host ""
