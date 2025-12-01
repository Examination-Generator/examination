# cPanel Production Deployment Setup

This document explains how to set up automatic deployment to cPanel production after Vercel staging.

## How It Works

1. **Push to main branch** → Triggers Vercel deployment (staging)
2. **Wait 10 minutes** → Allows time to verify staging and rollback if needed
3. **Auto-deploy to cPanel** → If no rollback, automatically deploys to production

## Required GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

### cPanel FTP Credentials
- `CPANEL_FTP_SERVER` - Your cPanel FTP server (e.g., `ftp.speedstarexams.co.ke` or `speedstarexams.co.ke`)
- `CPANEL_FTP_USERNAME` - Your cPanel FTP username (e.g., `zbhxqeap`)
- `CPANEL_FTP_PASSWORD` - Your cPanel FTP password

### Not Required (FTP-only deployment)
~~SSH credentials are not needed for FTP-only deployment~~

### cPanel Account Details
- `CPANEL_USERNAME` - Your cPanel account username (e.g., `zbhxqeap`)
- `CPANEL_DOMAIN` - Your production domain (e.g., `speedstarexams.co.ke`)

## cPanel Server Setup (One-Time Manual Setup)

### Option 1: Using cPanel Terminal (Recommended)

1. **Login to cPanel**
   - Go to `https://speedstarexams.co.ke:2083`
   - Login with username: `zbhxqeap`

2. **Open Terminal**
   - Search for "Terminal" in cPanel
   - Click to open

3. **Run setup script**
   ```bash
   cd ~/public_html/api
   bash setup.sh
   ```

4. **Edit .env file**
   - Use File Manager to edit `~/public_html/api/.env`
   - Add your SECRET_KEY and POSTGRES_URL

### Option 2: Using cPanel File Manager

If Terminal is not available, use File Manager:

1. **Create directories manually**
   - Create `/public_html/api` folder
   - Create `/public_html/api/venv` folder (Python will create this later)

2. **Upload files via FTP or File Manager**
   - Upload Django backend to `/public_html/api/`
   - Upload frontend build to `/public_html/`

3. **Setup Python App (if available)**
   - Go to "Setup Python App" in cPanel
   - Create app pointing to `/public_html/api`
   - Set Python version to 3.11 or higher
   - Set Application startup file to `passenger_wsgi.py`
   - Set Application Entry point to `application`

### Manual Setup Steps

#### 1. Create .env file
Create `~/public_html/api/.env` with:

```bash
SECRET_KEY=your-random-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=speedstarexams.co.ke,www.speedstarexams.co.ke
POSTGRES_URL=your-database-url-here
CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke,https://www.speedstarexams.co.ke
```

#### 2. Install Python packages
If cPanel has Terminal access:
```bash
cd ~/public_html/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Run migrations
```bash
source ~/public_html/api/venv/bin/activate
cd ~/public_html/api
python manage.py migrate --settings=examination_system.settings_production
```

#### 4. Collect static files
```bash
python manage.py collectstatic --noinput --settings=examination_system.settings_production
```

### Configuration Files (Auto-deployed by GitHub Actions)

The following files are automatically uploaded during deployment:

#### Frontend .htaccess
Location: `/public_html/.htaccess`
```apache
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
```

## Workflow Usage

### Normal Deployment
1. Push to main branch
2. Vercel deploys to staging
3. Test staging for 10 minutes
4. If OK, cPanel auto-deploys
5. If issues, cancel the GitHub Action workflow to stop cPanel deployment

### Manual Rollback Prevention
If you find issues in staging:
1. Go to GitHub Actions
2. Find the running "Deploy to cPanel Production" workflow
3. Click "Cancel workflow"
4. Fix the issue
5. Push again

### Manual Deployment
To manually trigger cPanel deployment:
1. Go to Actions tab
2. Select "Deploy to cPanel Production"
3. Click "Run workflow"
4. Select branch (usually `main`)
5. Click "Run workflow"

## Monitoring

Check deployment status:
- GitHub Actions tab shows deployment progress
- cPanel File Manager to verify files
- SSH to check logs: `tail -f ~/logs/error_log`

## Troubleshooting

### FTP Upload Issues
- Verify FTP credentials
- Check file permissions (should be 644 for files, 755 for directories)
- Ensure disk space available

### Python/Django Issues
- Check Python version: `python --version` (should be 3.11+)
- Verify virtual environment: `which python`
- Check Django settings: `python manage.py check --settings=examination_system.settings_production`

### Database Migration Issues
- SSH into server
- Activate venv: `source ~/public_html/api/venv/bin/activate`
- Run migrations manually: `python manage.py migrate --settings=examination_system.settings_production`

### Frontend Not Loading
- Check .htaccess file exists
- Verify build files are in public_html
- Check browser console for API URL errors

## Important Notes

⚠️ **Security**:
- Never commit secrets to Git
- Use strong passwords for cPanel
- Keep .env files secure
- Use HTTPS in production

⚠️ **Backup**:
- Always backup database before deployment
- Keep a copy of working code

⚠️ **Testing**:
- Always test on Vercel staging first
- Use the 10-minute window to verify everything works
- Have a rollback plan ready

## Support

If deployment fails:
1. Check GitHub Actions logs
2. Check cPanel error logs
3. Verify all secrets are set correctly
4. Test SSH/FTP access manually
