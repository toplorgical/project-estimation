# Quick System Verification Script
# Run this to check if your system is ready for Toplorgical

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Toplorgical System Verification" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true
$warnings = @()
$errorList = @()

# Function to check if a command exists
function Test-Command {
    param($command)
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Function to test port
function Test-Port {
    param($port)
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

# Check Python
Write-Host "[1/9] Checking Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "3\.1[1-9]|3\.[2-9]") {
        Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Python: $pythonVersion (3.11+ recommended)" -ForegroundColor Yellow
        $warnings += "Python version is older than 3.11"
    }
} else {
    Write-Host "  ❌ Python: NOT FOUND" -ForegroundColor Red
    $errorList += "Python is not installed"
    $allGood = $false
}

# Check Node.js
Write-Host "[2/9] Checking Node.js..." -ForegroundColor Yellow
if (Test-Command node) {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v1[8-9]|v[2-9]") {
        Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Node.js: $nodeVersion (v18+ recommended)" -ForegroundColor Yellow
        $warnings += "Node.js version is older than v18"
    }
} else {
    Write-Host "  ❌ Node.js: NOT FOUND" -ForegroundColor Red
    $errorList += "Node.js is not installed"
    $allGood = $false
}

# Check npm
Write-Host "[3/9] Checking npm..." -ForegroundColor Yellow
if (Test-Command npm) {
    $npmVersion = npm --version 2>&1
    Write-Host "  ✅ npm: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ npm: NOT FOUND" -ForegroundColor Red
    $errorList += "npm is not installed"
    $allGood = $false
}

# Check pip
Write-Host "[4/9] Checking pip..." -ForegroundColor Yellow
if (Test-Command pip) {
    $pipVersion = pip --version 2>&1 | Select-String -Pattern "pip (\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    Write-Host "  ✅ pip: v$pipVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ pip: NOT FOUND" -ForegroundColor Red
    $errorList += "pip is not installed"
    $allGood = $false
}

# Check PostgreSQL
Write-Host "[5/9] Checking PostgreSQL..." -ForegroundColor Yellow
if (Test-Command psql) {
    $pgVersion = psql --version 2>&1
    Write-Host "  ✅ PostgreSQL client: $pgVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  PostgreSQL client (psql) not found in PATH" -ForegroundColor Yellow
    $warnings += "PostgreSQL client tools not in PATH"
}

# Check if PostgreSQL server is running
$pgRunning = Test-Port 5432
if ($pgRunning) {
    Write-Host "  ✅ PostgreSQL server: Running on port 5432" -ForegroundColor Green
} else {
    Write-Host "  ❌ PostgreSQL server: Not running on port 5432" -ForegroundColor Red
    $errorList += "PostgreSQL server is not running"
    $allGood = $false
}

# Check Redis
Write-Host "[6/9] Checking Redis..." -ForegroundColor Yellow
$redisRunning = Test-Port 6379
if ($redisRunning) {
    Write-Host "  ✅ Redis: Running on port 6379" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Redis: Not running on port 6379" -ForegroundColor Yellow
    $warnings += "Redis is not running (optional but recommended)"
}

# Check project structure
Write-Host "[7/9] Checking project structure..." -ForegroundColor Yellow
$requiredPaths = @(
    "server\manage.py",
    "server\requirements.txt",
    "server\toplorgical\settings.py",
    "client\package.json",
    "client\src\main.tsx"
)

$structureOk = $true
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        Write-Host "  ❌ Missing: $path" -ForegroundColor Red
        $errorList += "Missing required file: $path"
        $structureOk = $false
        $allGood = $false
    }
}

if ($structureOk) {
    Write-Host "  ✅ Project structure: OK" -ForegroundColor Green
}

# Check environment files
Write-Host "[8/9] Checking environment files..." -ForegroundColor Yellow
$serverEnv = Test-Path "server\.env"
$clientEnv = Test-Path "client\.env"

if ($serverEnv) {
    Write-Host "  ✅ server/.env: EXISTS" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  server/.env: NOT FOUND (will use .env.example)" -ForegroundColor Yellow
    $warnings += "Backend .env file not found"
}

if ($clientEnv) {
    Write-Host "  ✅ client/.env: EXISTS" -ForegroundColor Green
} else {
    Write-Host "  ❌ client/.env: NOT FOUND" -ForegroundColor Red
    $errorList += "Frontend .env file not found"
    $allGood = $false
}

# Check port availability
Write-Host "[9/9] Checking port availability..." -ForegroundColor Yellow
$port8000 = Test-Port 8000
$port8080 = Test-Port 8080

if (-not $port8000) {
    Write-Host "  ✅ Port 8000: Available (backend)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Port 8000: In use" -ForegroundColor Yellow
    $warnings += "Port 8000 is already in use"
}

if (-not $port8080) {
    Write-Host "  ✅ Port 8080: Available (frontend)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Port 8080: In use" -ForegroundColor Yellow
    $warnings += "Port 8080 is already in use"
}

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Verification Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    if ($warnings.Count -eq 0) {
        Write-Host "✅ READY TO RUN!" -ForegroundColor Green
        Write-Host ""
        Write-Host "All checks passed! Your system is ready." -ForegroundColor Green
        Write-Host ""
        Write-Host "To start the application, run:" -ForegroundColor Cyan
        Write-Host "  .\start.ps1" -ForegroundColor White
    } else {
        Write-Host "✅ READY (with warnings)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  • $warning" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "You can proceed, but some features may not work." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To start the application, run:" -ForegroundColor Cyan
        Write-Host "  .\start.ps1" -ForegroundColor White
    }
} else {
    Write-Host "❌ NOT READY" -ForegroundColor Red
    Write-Host ""
    Write-Host "Critical errors found:" -ForegroundColor Red
    foreach ($err in $errorList) {
        Write-Host "  • $err" -ForegroundColor Red
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  • $warning" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Please fix the errors above before running the application." -ForegroundColor Red
    Write-Host ""
    Write-Host "See CHECKLIST.md for installation instructions." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Pause
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
