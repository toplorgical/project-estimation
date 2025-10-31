# Toplorgical Frontend Startup Script for Windows
# This script checks prerequisites and starts the Vite development server

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Toplorgical Frontend Startup Script" -ForegroundColor Cyan
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

# Check Node.js
Write-Host "[1/5] Checking Node.js..." -ForegroundColor Yellow
if (Test-Command node) {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js $nodeVersion found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js not found. Please install Node.js 18+!" -ForegroundColor Red
    exit 1
}

# Check package manager (npm or bun)
Write-Host "[2/5] Checking package manager..." -ForegroundColor Yellow
$packageManager = "npm"
if (Test-Command bun) {
    $packageManager = "bun"
    $bunVersion = bun --version
    Write-Host "  ✓ Bun $bunVersion found (will use bun)" -ForegroundColor Green
} elseif (Test-Command npm) {
    $npmVersion = npm --version
    Write-Host "  ✓ npm $npmVersion found (will use npm)" -ForegroundColor Green
} else {
    Write-Host "  ✗ No package manager found!" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
Write-Host "[3/5] Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  ✓ Dependencies appear to be installed" -ForegroundColor Green
} else {
    Write-Host "  ! Installing dependencies..." -ForegroundColor Yellow
    if ($packageManager -eq "bun") {
        bun install
    } else {
        npm install
    }
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
}

# Check if .env file exists
Write-Host "[4/5] Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
    
    # Display API URL
    $apiUrl = Select-String -Path ".env" -Pattern "VITE_API_BASE_URL=" | ForEach-Object { $_.Line.Split('=')[1] }
    if ($apiUrl) {
        Write-Host "  API Base URL: $apiUrl" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please create a .env file based on .env.example" -ForegroundColor Yellow
    exit 1
}

# Check if backend is running
Write-Host "[5/5] Checking backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Backend is running and responding" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Backend is not responding at http://localhost:8000" -ForegroundColor Yellow
    Write-Host "  Make sure to start the backend server first!" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Check if port is available
Write-Host ""
Write-Host "Checking available ports..." -ForegroundColor Yellow
$port = 8080
$ports = @(8080, 3000, 5173, 4173, 5000)
$foundPort = $false

foreach ($p in $ports) {
    if (-not (Test-Port $p)) {
        $port = $p
        $foundPort = $true
        Write-Host "  ✓ Port $port is available" -ForegroundColor Green
        break
    }
}

if (-not $foundPort) {
    Write-Host "  ⚠ All common ports are in use. Vite will find an available port." -ForegroundColor Yellow
}

# Start the development server
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Starting Vite Development Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor Green
Write-Host "  • Local: http://localhost:$port" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Vite server
if ($packageManager -eq "bun") {
    bun run dev --port $port
} else {
    npm run dev -- --port $port
}
