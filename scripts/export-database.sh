#!/bin/bash

# Export PostgreSQL Database to SQL file
# This exports the local database that was synced from Vercel

set -e

echo "============================================"
echo "DATABASE EXPORT: Local PostgreSQL"
echo "============================================"
echo ""

# Database credentials from .env
DB_NAME="examination_system"
DB_USER="postgres"
EXPORT_FILE="vercel_to_cpanel_backup.sql"

echo "📦 Exporting database: $DB_NAME"
echo "👤 User: $DB_USER"
echo "📄 Output file: $EXPORT_FILE"
echo ""

# Check if pg_dump is available
if ! command -v pg_dump &> /dev/null; then
    echo "❌ Error: pg_dump not found"
    echo "Please install PostgreSQL client tools"
    exit 1
fi

echo "⏳ Exporting database..."
pg_dump -U "$DB_USER" -d "$DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    > "$EXPORT_FILE"

if [ $? -eq 0 ]; then
    FILE_SIZE=$(du -h "$EXPORT_FILE" | cut -f1)
    echo ""
    echo "============================================"
    echo "✅ EXPORT COMPLETE!"
    echo "============================================"
    echo "File: $EXPORT_FILE"
    echo "Size: $FILE_SIZE"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to cPanel → phpPgAdmin"
    echo "2. Select database: zbhxqeap_exam"
    echo "3. Click 'SQL' tab"
    echo "4. Upload/paste $EXPORT_FILE"
    echo "5. Execute the SQL"
    echo ""
    echo "Or upload via FTP to cPanel and contact support to restore it."
else
    echo ""
    echo "❌ Export failed!"
    exit 1
fi
