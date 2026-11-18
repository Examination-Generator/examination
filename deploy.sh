#!/bin/bash
set -e

APP_DIR="/var/www/examination"
BACKEND_DIR="$APP_DIR/django_backend"
FRONTEND_DIR="$APP_DIR/frontend/exam"

echo "==> Pulling latest code..."
cd "$APP_DIR"
git pull origin main

echo "==> Loading environment variables..."
set -a
source "$APP_DIR/.env.deploy"
set +a

echo "==> Updating backend dependencies..."
cd "$BACKEND_DIR"
source venv/bin/activate
pip install -r requirements.txt

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Building frontend..."
cd "$FRONTEND_DIR"
npm install
if [ -d build ]; then
    chmod -R u+rwX build
fi
npm run build

echo "==> Fixing permissions..."
# Nginx (www-data) must be able to traverse the parent folders
chmod o+x "$APP_DIR" "$APP_DIR/frontend" "$FRONTEND_DIR" "$BACKEND_DIR"
chmod -R o+rX "$FRONTEND_DIR/build"
chmod -R o+rX "$BACKEND_DIR/staticfiles"

echo "==> Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "==> Deploy complete."