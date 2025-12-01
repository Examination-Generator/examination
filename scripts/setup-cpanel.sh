#!/bin/bash

# cPanel Initial Setup Script
# Run this script on your cPanel server via SSH

set -e

echo "=================================================="
echo "cPanel Production Server Setup"
echo "=================================================="
echo ""

# Get user input
read -p "Enter your cPanel username: " CPANEL_USER
read -p "Enter your domain name (e.g., yourdomain.com): " DOMAIN
read -p "Enter your database URL: " DATABASE_URL
read -sp "Enter Django SECRET_KEY: " SECRET_KEY
echo ""

# Set paths
API_DIR="/home/$CPANEL_USER/public_html/api"
WEB_DIR="/home/$CPANEL_USER/public_html"

echo ""
echo "📁 Creating directory structure..."
mkdir -p "$API_DIR"
mkdir -p "$WEB_DIR"
cd "$API_DIR"

echo "🐍 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📝 Creating .env file..."
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
POSTGRES_URL=$DATABASE_URL
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
EOF

echo "🔧 Creating passenger_wsgi.py..."
cat > passenger_wsgi.py << EOF
import sys
import os

# Add your project directory to the sys.path
project_home = '$API_DIR'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'examination_system.settings_production'

# Import Django application
from examination_system.wsgi import application
EOF

echo "📄 Creating API .htaccess..."
cat > .htaccess << 'EOF'
RewriteEngine On
RewriteBase /api/
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]
EOF

echo "📄 Creating frontend .htaccess..."
cat > "$WEB_DIR/.htaccess" << 'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-XSS-Protection "1; mode=block"
</IfModule>
EOF

echo "🔒 Setting permissions..."
chmod 644 .env
chmod 644 passenger_wsgi.py
chmod 644 .htaccess
chmod 644 "$WEB_DIR/.htaccess"
chmod 755 "$API_DIR"
chmod 755 "$WEB_DIR"

echo ""
echo "✅ cPanel server setup completed!"
echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo "1. Add these GitHub Secrets in your repository:"
echo "   - CPANEL_FTP_SERVER (FTP server address)"
echo "   - CPANEL_FTP_USERNAME (FTP username)"
echo "   - CPANEL_FTP_PASSWORD (FTP password)"
echo "   - CPANEL_SSH_HOST ($DOMAIN)"
echo "   - CPANEL_SSH_USERNAME ($CPANEL_USER)"
echo "   - CPANEL_SSH_PASSWORD (Your SSH password)"
echo "   - CPANEL_SSH_PORT (Usually 22)"
echo "   - CPANEL_USERNAME ($CPANEL_USER)"
echo "   - CPANEL_DOMAIN ($DOMAIN)"
echo "   - CPANEL_API_URL (https://$DOMAIN/api)"
echo ""
echo "2. Push to main branch to trigger deployment"
echo ""
echo "3. Monitor deployment in GitHub Actions tab"
echo ""
echo "=================================================="
echo "Directory Structure:"
echo "=================================================="
echo "API: $API_DIR"
echo "Frontend: $WEB_DIR"
echo ""
echo "Files created:"
echo " - $API_DIR/.env"
echo " - $API_DIR/passenger_wsgi.py"
echo " - $API_DIR/.htaccess"
echo " - $WEB_DIR/.htaccess"
echo ""
