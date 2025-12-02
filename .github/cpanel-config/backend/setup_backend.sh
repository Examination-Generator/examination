#!/bin/bash
# Automated setup script for cPanel backend
# Run this via cPanel Terminal after deployment

# Set variables
APP_DIR="/home/zbhxqeap/public_html/api"
VENV_DIR="$APP_DIR/venv"

cd $APP_DIR || exit 1

echo "🔧 Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3.11 -m venv $VENV_DIR || python3 -m venv $VENV_DIR
fi

echo "📦 Installing dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "📝 Creating .env file..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
SECRET_KEY=django-insecure-replace-this-with-actual-secret-key
DEBUG=False
ALLOWED_HOSTS=speedstarexams.co.ke,51.91.24.182
DATABASE_URL=postgresql://zbhxqeap_editor:TesterK&700@localhost:5432/zbhxqeap_exam
CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke
EOF
    echo "⚠️  Please update SECRET_KEY in .env file!"
fi

echo "🗄️  Running database migrations..."
python manage.py migrate --settings=examination_system.settings_production

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=examination_system.settings_production

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update SECRET_KEY in .env file"
echo "2. Restart Python application in cPanel"
echo "3. Test: curl https://speedstarexams.co.ke/api/"
