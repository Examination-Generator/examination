# Database Sync Script: Vercel → cPanel
# This script syncs all data from Vercel Postgres to cPanel PostgreSQL

# Check if VERCEL_DB_URL is provided
if ($args.Count -eq 0) {
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host "DATABASE SYNC: Vercel → cPanel" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "❌ Error: Vercel database URL required" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:"
    Write-Host '  .\scripts\sync-database.ps1 "postgresql://user:pass@host:port/db"'
    Write-Host ""
    Write-Host "Get your Vercel database URL from:"
    Write-Host "  1. Go to Vercel Dashboard → Your Project"
    Write-Host "  2. Click 'Storage' → Your Postgres Database"
    Write-Host "  3. Copy the 'POSTGRES_URL' connection string"
    Write-Host ""
    exit 1
}

$VERCEL_DB_URL = $args[0]
$DRY_RUN = $args[1]

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DATABASE SYNC: Vercel → cPanel" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to django_backend directory
Set-Location "$PSScriptRoot\..\django_backend"

Write-Host "📋 Step 1: Installing dependencies..." -ForegroundColor Yellow
pip install -q psycopg2-binary

Write-Host ""
Write-Host "📋 Step 2: Checking database connections..." -ForegroundColor Yellow

if ($DRY_RUN -eq "--dry-run") {
    python manage.py sync_vercel_to_cpanel --vercel-db-url="$VERCEL_DB_URL" --dry-run
} else {
    Write-Host ""
    Write-Host "⚠️  WARNING: This will sync all data from Vercel to cPanel!" -ForegroundColor Yellow
    Write-Host "⚠️  Existing data in cPanel will be replaced." -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Continue? (yes/no)"
    
    if ($confirm -eq "yes") {
        python manage.py sync_vercel_to_cpanel --vercel-db-url="$VERCEL_DB_URL"
    } else {
        Write-Host "❌ Sync cancelled" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green
