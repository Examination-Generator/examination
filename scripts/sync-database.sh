#!/bin/bash

# Database Sync Script: Vercel → cPanel
# This script syncs all data from Vercel Postgres to cPanel PostgreSQL

set -e

echo "============================================"
echo "DATABASE SYNC: Vercel → cPanel"
echo "============================================"
echo ""

# Check if VERCEL_DB_URL is provided
if [ -z "$1" ]; then
    echo "❌ Error: Vercel database URL required"
    echo ""
    echo "Usage:"
    echo "  ./scripts/sync-database.sh 'postgresql://user:pass@host:port/db'"
    echo ""
    echo "Get your Vercel database URL from:"
    echo "  1. Go to Vercel Dashboard → Your Project"
    echo "  2. Click 'Storage' → Your Postgres Database"
    echo "  3. Copy the 'POSTGRES_URL' connection string"
    echo ""
    exit 1
fi

VERCEL_DB_URL="$1"
DRY_RUN="${2:-false}"

# Navigate to django_backend directory
cd "$(dirname "$0")/../django_backend"

echo "📋 Step 1: Installing dependencies..."
pip install -q psycopg2-binary

echo ""
echo "📋 Step 2: Setting up Django environment..."
export DJANGO_SETTINGS_MODULE=examination_system.settings

echo ""
echo "📋 Step 3: Checking database connections..."
if [ "$DRY_RUN" = "--dry-run" ]; then
    python manage.py sync_vercel_to_cpanel --vercel-db-url="$VERCEL_DB_URL" --dry-run
else
    echo ""
    echo "⚠️  WARNING: This will sync all data from Vercel to cPanel!"
    echo "⚠️  Existing data in cPanel will be replaced."
    echo ""
    read -p "Continue? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        python manage.py sync_vercel_to_cpanel --vercel-db-url="$VERCEL_DB_URL"
    else
        echo "❌ Sync cancelled"
        exit 1
    fi
fi

echo ""
echo "✅ Done!"
