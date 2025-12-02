#!/bin/bash

# Quick Setup Script for cPanel Python App
# Run these commands in the cPanel Terminal (if available) or follow manually

echo "==================================="
echo "cPanel Python App Setup Assistant"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found!"
    echo "Please run this script from /home/zbhxqeap/public_html/api/"
    exit 1
fi

echo "✅ Found manage.py - in correct directory"
echo ""

# Check for virtual environment
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    source venv/bin/activate
else
    echo "❌ Virtual environment not found"
    echo "The Python App should have created this automatically"
    echo "Please check Python App configuration in cPanel"
    exit 1
fi

# Check Python version
echo ""
echo "Python Information:"
python --version
which python
echo ""

# Check if Django is installed
if python -c "import django" 2>/dev/null; then
    echo "✅ Django is installed"
    python -c "import django; print(f'   Version: {django.get_version()}')"
else
    echo "❌ Django not installed"
    echo "Run 'RUN PIP INSTALL' in cPanel Python App interface"
    exit 1
fi

# Check environment variables
echo ""
echo "Checking environment variables..."
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY not set"
else
    echo "✅ SECRET_KEY is set"
fi

if [ -z "$DB_NAME" ]; then
    echo "❌ DB_NAME not set"
else
    echo "✅ DB_NAME is set: $DB_NAME"
fi

# Check database connection
echo ""
echo "Testing database connection..."
python manage.py check --database default --settings=examination_system.settings_production

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo "Check your database credentials in environment variables"
    exit 1
fi

# Check for pending migrations
echo ""
echo "Checking for pending migrations..."
python manage.py showmigrations --settings=examination_system.settings_production

# Ask user if they want to run migrations
echo ""
read -p "Do you want to run migrations now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py migrate --settings=examination_system.settings_production
    echo "✅ Migrations completed"
fi

# Collect static files
echo ""
read -p "Do you want to collect static files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py collectstatic --noinput --settings=examination_system.settings_production
    echo "✅ Static files collected"
fi

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Go to cPanel → Software → Setup Python App"
echo "2. Click RESTART on your application"
echo "3. Visit: https://speedstarexams.co.ke/api/"
echo ""
echo "Expected result: Django REST framework page"
echo ""
