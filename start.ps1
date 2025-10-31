# Master Startup Script for Toplorgical Platform
# This script starts both backend and frontend in separate windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Toplorgical Platform Launcher" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot

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

# Quick prerequisite check
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$allGood = $true

# Check Python
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    $allGood = $false
}

# Check Node.js
if (Test-Command node) {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js not found!" -ForegroundColor Red
    $allGood = $false
}

# Check PostgreSQL (try to connect to default port)
Write-Host "  • PostgreSQL: Checking..." -NoNewline
$pgCheck = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue -InformationLevel Quiet
if ($pgCheck) {
    Write-Host "`r  ✓ PostgreSQL: Running on port 5432" -ForegroundColor Green
} else {
    Write-Host "`r  ⚠ PostgreSQL: Not detected on port 5432" -ForegroundColor Yellow
    Write-Host "    Make sure PostgreSQL is running!" -ForegroundColor Yellow
}

# Check Redis
Write-Host "  • Redis: Checking..." -NoNewline
$redisCheck = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue -InformationLevel Quiet
if ($redisCheck) {
    Write-Host "`r  ✓ Redis: Running on port 6379" -ForegroundColor Green
} else {
    Write-Host "`r  ⚠ Redis: Not detected on port 6379" -ForegroundColor Yellow
    Write-Host "    Redis is optional but recommended!" -ForegroundColor Yellow
}

Write-Host ""

if (-not $allGood) {
    Write-Host "Please install missing prerequisites before continuing." -ForegroundColor Red
    Write-Host "See SETUP.md for installation instructions." -ForegroundColor Yellow
    exit 1
}

# Ask user what to start
Write-Host "What would you like to start?" -ForegroundColor Cyan
Write-Host "  [1] Backend only (Django API)" -ForegroundColor White
Write-Host "  [2] Frontend only (React App)" -ForegroundColor White
Write-Host "  [3] Both Backend and Frontend (Recommended)" -ForegroundColor White
Write-Host "  [4] Exit" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Backend..." -ForegroundColor Green
        Write-Host ""
        Set-Location "$projectRoot\server"
        Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start-local.ps1"
        Write-Host "Backend started in a new window." -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Frontend..." -ForegroundColor Green
        Write-Host ""
        Set-Location "$projectRoot\client"
        Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start-local.ps1"
        Write-Host "Frontend started in a new window." -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "Starting Backend and Frontend..." -ForegroundColor Green
        Write-Host ""
        
        # Start backend
        Write-Host "  • Launching Backend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$projectRoot\server\start-local.ps1"
        
        # Wait a moment before starting frontend
        Write-Host "  • Waiting for backend to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        # Start frontend
        Write-Host "  • Launching Frontend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$projectRoot\client\start-local.ps1"
        
        Write-Host ""
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host "  Both services started successfully!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Services are running in separate windows:" -ForegroundColor White
        Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  • Frontend App: http://localhost:8080" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Useful URLs:" -ForegroundColor White
        Write-Host "  • API Docs: http://localhost:8000/api/docs/" -ForegroundColor Cyan
        Write-Host "  • Admin Panel: http://localhost:8000/admin/" -ForegroundColor Cyan
        Write-Host "  • Health Check: http://localhost:8000/health/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To stop the services, close the PowerShell windows or press Ctrl+C" -ForegroundColor Yellow
    }
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
