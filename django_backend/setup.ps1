# Django Backend Setup Script for Windows PowerShell
# Run this script to automatically setup the Django backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Django Backend Setup Script" -ForegroundColor Cyan
Write-Host "Examination System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host " [OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " [✗] Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if PostgreSQL is accessible
Write-Host ""
Write-Host "[2/8] Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    Write-Host " [OK] PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host " [✗] PostgreSQL not found. Please install PostgreSQL." -ForegroundColor Red
    Write-Host "  Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "  Or install pgAdmin: https://www.pgadmin.org/download/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[3/8] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host " [OK] Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host " [OK] Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[4/8] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host " [OK] Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[5/8] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
pip install -r requirements.txt --quiet
Write-Host " [OK] Dependencies installed" -ForegroundColor Green

# Check if .env exists
Write-Host ""
Write-Host "[6/8] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host " [OK] .env file found" -ForegroundColor Green
} else {
    Write-Host "! .env not found, copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host " [OK] .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "[⚠] IMPORTANT: Update .env with your PostgreSQL password!" -ForegroundColor Yellow
    Write-Host "  Open .env and change DB_PASSWORD=postgres to your password" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Press Enter to continue after updating .env, or 'skip' to continue anyway"
}

# Create database
Write-Host ""
Write-Host "[7/8] Setting up database..." -ForegroundColor Yellow
Write-Host "  You may be prompted for PostgreSQL password" -ForegroundColor Gray

$dbExists = $false
try {
    $checkDb = psql -U postgres -lqt 2>&1 | Select-String -Pattern "examination_system"
    if ($checkDb) {
        Write-Host " [OK] Database 'examination_system' already exists" -ForegroundColor Green
        $dbExists = $true
    }
} catch {
    Write-Host "[!]Could not check database status" -ForegroundColor Yellow
}

if (-not $dbExists) {
    Write-Host "  Creating database..." -ForegroundColor Gray
    try {
        psql -U postgres -c "CREATE DATABASE examination_system;" 2>&1 | Out-Null
        Write-Host " [OK] Database 'examination_system' created" -ForegroundColor Green
    } catch {
        Write-Host "[!] Could not create database automatically" -ForegroundColor Yellow
        Write-Host "  Please create it manually in pgAdmin or psql:" -ForegroundColor Gray
        Write-Host "  CREATE DATABASE examination_system;" -ForegroundColor Gray
    }
}

# Run migrations
Write-Host ""
Write-Host "[8/8] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate
Write-Host " [OK] Migrations completed" -ForegroundColor Green

# Success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " [OK] Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Create superuser (optional):" -ForegroundColor White
Write-Host "     python manage.py createsuperuser" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start development server:" -ForegroundColor White
Write-Host "     python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Access the application:" -ForegroundColor White
Write-Host "     API: http://127.0.0.1:8000/api/" -ForegroundColor Gray
Write-Host "     Swagger: http://127.0.0.1:8000/swagger/" -ForegroundColor Gray
Write-Host "     Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Gray
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Yellow
Write-Host ""
