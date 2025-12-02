# Environment Verification Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Speak-Sync Environment Verification  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$hasErrors = $false

# Check .env file
Write-Host "[1/6] Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  SUCCESS: .env file found" -ForegroundColor Green
} else {
    Write-Host "  ERROR: .env file not found" -ForegroundColor Red
    $hasErrors = $true
}

# Verify environment variables
Write-Host ""
Write-Host "[2/6] Verifying environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content .env
    $requiredVars = @("DATABASE_URL", "REDIS_URL", "RABBITMQ_URL", "JWT_ACCESS_SECRET", "JWT_REFRESH_SECRET", "INTERNAL_API_KEY")
    foreach ($var in $requiredVars) {
        $found = $envContent | Select-String -Pattern "^$var=" -Quiet
        if ($found) {
            Write-Host "  SUCCESS: $var configured" -ForegroundColor Green
        } else {
            Write-Host "  ERROR: $var missing" -ForegroundColor Red
            $hasErrors = $true
        }
    }
}

# Check Node.js
Write-Host ""
Write-Host "[3/6] Checking Node.js environment..." -ForegroundColor Yellow
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVersion = node --version
    Write-Host "  SUCCESS: Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Node.js not found" -ForegroundColor Red
    $hasErrors = $true
}

$pnpmCmd = Get-Command pnpm -ErrorAction SilentlyContinue
if ($pnpmCmd) {
    $pnpmVersion = pnpm --version
    Write-Host "  SUCCESS: pnpm $pnpmVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: pnpm not found" -ForegroundColor Red
    $hasErrors = $true
}

# Check Python
Write-Host ""
Write-Host "[4/6] Checking Python environment..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = python --version
    Write-Host "  SUCCESS: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python not found" -ForegroundColor Red
    $hasErrors = $true
}

# Check Docker
Write-Host ""
Write-Host "[5/6] Checking Docker..." -ForegroundColor Yellow
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    $dockerVersion = docker --version
    Write-Host "  SUCCESS: Docker installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Docker not found" -ForegroundColor Red
    $hasErrors = $true
}

# Check dependencies
Write-Host ""
Write-Host "[6/6] Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  SUCCESS: Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Run pnpm install" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($hasErrors) {
    Write-Host "  WARNING: Some issues found" -ForegroundColor Yellow
} else {
    Write-Host "  SUCCESS: All checks passed!" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
