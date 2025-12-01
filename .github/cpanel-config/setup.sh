#!/bin/bash

# cPanel Manual Setup Script for speedstarexams.co.ke
# Run this script once via cPanel Terminal after the first deployment

echo "========================================="
echo "Setting up Django on cPanel"
echo "========================================="

# Navigate to API directory
cd ~/public_html/api || exit

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
SECRET_KEY=change-this-to-a-random-secret-key
DEBUG=False
ALLOWED_HOSTS=speedstarexams.co.ke,www.speedstarexams.co.ke
POSTGRES_URL=your-database-url-here
CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke,https://www.speedstarexams.co.ke
EOF
    echo "⚠️  IMPORTANT: Edit .env file and add your SECRET_KEY and POSTGRES_URL"
else
    echo ".env file already exists"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=examination_system.settings_production

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=examination_system.settings_production

echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit ~/public_html/api/.env with your SECRET_KEY and database URL"
echo "2. Restart your app from cPanel (if using Python app manager)"
echo "3. Visit https://speedstarexams.co.ke to test"
echo ""
