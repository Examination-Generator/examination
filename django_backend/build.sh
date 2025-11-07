#!/bin/bash
# Build script for Vercel deployment with automatic migrations

echo "==================== BUILD SCRIPT STARTED ===================="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files (suppress errors if no static files)
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear || true

# CRITICAL: Run database migrations automatically
echo "==================== RUNNING DATABASE MIGRATIONS ===================="
python manage.py migrate --noinput --settings=examination_system.settings_production || {
    echo "ERROR: Migration failed! Check if POSTGRES_URL is set correctly."
    exit 1
}

echo "==================== MIGRATIONS COMPLETED SUCCESSFULLY ===================="

# Create default admin and editor users
echo "==================== CREATING DEFAULT USERS ===================="
python manage.py create_default_users --settings=examination_system.settings_production || {
    echo "WARNING: Failed to create default users, but continuing..."
}

echo "==================== DEFAULT USERS SETUP COMPLETED ===================="
echo "==================== BUILD SCRIPT COMPLETED ===================="
