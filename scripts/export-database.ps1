# Export PostgreSQL Database to SQL file
# This exports the local database that was synced from Vercel

# Database credentials from .env
$DB_NAME = "examination_system"
$DB_USER = "postgres"
$EXPORT_FILE = "vercel_to_cpanel_backup.sql"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DATABASE EXPORT: Local PostgreSQL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Exporting database: $DB_NAME" -ForegroundColor Yellow
Write-Host "👤 User: $DB_USER" -ForegroundColor Yellow
Write-Host "📄 Output file: $EXPORT_FILE" -ForegroundColor Yellow
Write-Host ""

# Check if pg_dump is available
$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if (-not $pgDump) {
    Write-Host "❌ Error: pg_dump not found" -ForegroundColor Red
    Write-Host "Please install PostgreSQL client tools" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Exporting database..." -ForegroundColor Yellow

# Run pg_dump
pg_dump -U $DB_USER -d $DB_NAME --clean --if-exists --no-owner --no-privileges | Out-File -FilePath $EXPORT_FILE -Encoding UTF8

if ($LASTEXITCODE -eq 0) {
    $fileSize = (Get-Item $EXPORT_FILE).Length / 1KB
    $fileSizeFormatted = "{0:N2} KB" -f $fileSize
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "✅ EXPORT COMPLETE!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "File: $EXPORT_FILE" -ForegroundColor Green
    Write-Host "Size: $fileSizeFormatted" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Go to cPanel → phpPgAdmin"
    Write-Host "2. Select database: zbhxqeap_exam"
    Write-Host "3. Click 'SQL' tab"
    Write-Host "4. Upload/paste $EXPORT_FILE"
    Write-Host "5. Execute the SQL"
    Write-Host ""
    Write-Host "Or upload via FTP to cPanel and contact support to restore it."
} else {
    Write-Host ""
    Write-Host "❌ Export failed!" -ForegroundColor Red
    exit 1
}
