#!/bin/bash
set -e

echo "==> Pulling latest code..."
cd /var/www/examination
git pull origin main

echo "==> Loading environment variables..."
set -a
source /var/www/examination/.env.deploy
set +a

echo "==> Updating backend dependencies..."
cd /var/www/examination/django_backend
source venv/bin/activate
pip install -r requirements.txt

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Building frontend..."
cd /var/www/examination/frontend/exam
npm install
npm run build

echo "==> Fixing permissions..."
chmod -R o+rX /var/www/examination/frontend/exam/build
chmod -R o+rX /var/www/examination/django_backend/staticfiles

echo "==> Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "==> Deploy complete."
