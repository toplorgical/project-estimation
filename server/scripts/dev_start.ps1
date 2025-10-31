# Simple dev start script for Windows PowerShell
# 1) Activates venv if present
# 2) Runs init (migrate + ensure superuser + seed once)
# 3) Starts Django dev server

param(
    [string]$Email = "admin@local",
    [string]$Password = "admin123",
    [string]$Username = "admin",
    [string]$FirstName = "Admin",
    [string]$LastName = "User",
    [switch]$UseSqlite
)

$ErrorActionPreference = "Stop"

# Activate venv if exists
if (Test-Path -Path "./venv/Scripts/Activate.ps1") {
    . ./venv/Scripts/Activate.ps1
}

# Export env vars for superuser and DB
$env:DJANGO_SUPERUSER_EMAIL = $Email
$env:DJANGO_SUPERUSER_PASSWORD = $Password
$env:DJANGO_SUPERUSER_USERNAME = $Username
$env:DJANGO_SUPERUSER_FIRST_NAME = $FirstName
$env:DJANGO_SUPERUSER_LAST_NAME = $LastName

if ($UseSqlite) {
    $env:USE_SQLITE = "True"
}

# Initialize app (idempotent)
python manage.py init_app

# Start server
python manage.py runserver 0.0.0.0:8000
