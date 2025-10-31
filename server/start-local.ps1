# Toplorgical Backend Startup Script for Windows
# This script checks prerequisites and starts the Django development server

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Toplorgical Backend Startup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

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

# Function to check if a port is in use
function Test-Port {
    param($port)
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

# Check Python
Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "  ✓ $pythonVersion found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found. Please install Python 3.11+!" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
Write-Host "[2/7] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "  ! Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[3/7] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Check if dependencies are installed
Write-Host "[4/7] Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list 2>&1
if ($pipList -match "Django") {
    Write-Host "  ✓ Dependencies appear to be installed" -ForegroundColor Green
} else {
    Write-Host "  ! Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
}

# Check if .env file exists
Write-Host "[5/7] Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "  ✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please create a .env file based on .env.example" -ForegroundColor Yellow
    exit 1
}

# Check if logs directory exists
if (-not (Test-Path "logs")) {
    Write-Host "  ! Creating logs directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path logs | Out-Null
    Write-Host "  ✓ Logs directory created" -ForegroundColor Green
}

# Check PostgreSQL connection
Write-Host "[6/7] Checking database connection..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "toplorgical.settings"
$dbCheck = python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toplorgical.settings'); from django.db import connection; connection.ensure_connection(); print('OK')" 2>&1
if ($dbCheck -match "OK") {
    Write-Host "  ✓ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ Database connection failed!" -ForegroundColor Red
    Write-Host "  Please ensure PostgreSQL is running and credentials are correct in .env" -ForegroundColor Yellow
    Write-Host "  Error: $dbCheck" -ForegroundColor Red
    exit 1
}

# Run migrations
Write-Host "[7/7] Running migrations..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations completed successfully" -ForegroundColor Green
} else {
    Write-Host "  ! Migrations had warnings/errors (check output above)" -ForegroundColor Yellow
}

# Check if port 8000 is available
Write-Host ""
Write-Host "Checking if port 8000 is available..." -ForegroundColor Yellow
if (Test-Port 8000) {
    Write-Host "  ⚠ Warning: Port 8000 is already in use!" -ForegroundColor Red
    Write-Host "  Please stop the existing process or use a different port." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To find what's using port 8000:" -ForegroundColor Cyan
    Write-Host "  netstat -ano | findstr :8000" -ForegroundColor White
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Start the server
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Starting Django Development Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "  • Frontend: http://localhost:8000" -ForegroundColor White
Write-Host "  • API: http://localhost:8000/api/v1/" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host "  • Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Django server
python manage.py runserver 0.0.0.0:8000
