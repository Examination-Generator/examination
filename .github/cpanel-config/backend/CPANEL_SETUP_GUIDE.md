# cPanel Python App Setup Guide

This guide covers the **one-time manual setup** required for the cPanel Python application. After this initial setup, all deployments are automatic via GitHub Actions.

---

## 🎯 One-Time Setup (Manual)

### Step 1: Create Python Application in cPanel

1. **Login to cPanel** at `https://speedstarexams.co.ke:2083`
2. Navigate to **Software → Setup Python App**
3. Click **CREATE APPLICATION**
4. Configure the application:
   ```
   Python version:        3.13.5 (or latest available)
   Application root:      api
   Application URL:       speedstarexams.co.ke/api
   Application startup file: passenger_wsgi.py
   Application Entry point: application
   ```
5. Click **CREATE**
6. **IMPORTANT**: After creation, the Python app will auto-generate a `passenger_wsgi.py` file. **Delete this auto-generated file** as our deployment will provide the correct one.

### Step 2: Create Environment Variables

In the Python App interface, add these environment variables by clicking **EDIT** on the application:

```bash
SECRET_KEY=your-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=speedstarexams.co.ke,www.speedstarexams.co.ke,51.91.24.182

# Database Configuration
DB_NAME=zbhxqeap_exam
DB_USER=zbhxqeap_editor
DB_PASSWORD=TesterK&700
DB_HOST=localhost
DB_PORT=5432

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke,https://www.speedstarexams.co.ke
```

**To generate a secure SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 3: Create `.env` File (Backup)

While environment variables are set in the Python App interface, create a backup `.env` file in `/home/zbhxqeap/public_html/api/.env`:

1. Go to **Files → File Manager**
2. Navigate to `public_html/api/`
3. Click **+ File** and name it `.env`
4. Edit the file and paste the same environment variables as above

### Step 4: Install Dependencies

1. In the Python App interface, click **RUN PIP INSTALL**
2. Wait for all packages from `requirements.txt` to install
3. Verify installation completed successfully

### Step 5: Initial Migration (One-time)

**Important**: The first deployment requires a manual migration to set up the database schema.

1. In the Python App interface, under **Execute Python script**, run:
   ```python
   import os
   import django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')
   django.setup()
   from django.core.management import call_command
   call_command('migrate', '--noinput')
   print("✅ Migrations completed!")
   ```

2. Alternatively, if you have SSH access, run:
   ```bash
   cd /home/zbhxqeap/public_html/api
   source venv/bin/activate
   python manage.py migrate --settings=examination_system.settings_production
   ```

### Step 6: Collect Static Files (One-time)

Run this in **Execute Python script**:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')
django.setup()
from django.core.management import call_command
call_command('collectstatic', '--noinput')
print("✅ Static files collected!")
```

### Step 7: Restart Application

Click the **RESTART** button in the Python App interface.

---

## 🚀 Automatic Deployments

After the one-time setup above, all future deployments are **100% automatic**:

1. **Push to GitHub** → Triggers workflow
2. **10-minute wait** → Time to verify Vercel staging
3. **Frontend deployment** → React build deployed to `public_html/`
4. **Backend deployment** → Django code deployed to `public_html/api/`
5. **Auto-migration** → Database automatically updates on first request
6. **Auto-restart** → Application automatically picks up new code

### What Gets Deployed Automatically:

✅ Django backend code (`django_backend/` → `public_html/api/`)  
✅ `passenger_wsgi.py` (with improved error handling)  
✅ `requirements.txt` (install manually via "Run Pip Install" if dependencies change)  
✅ Frontend build (`frontend/exam/build/` → `public_html/`)  
✅ `.htaccess` files (for React routing and Python app)  

### What Is Preserved (Never Overwritten):

🔒 `venv/` - Virtual environment  
🔒 `.env` - Environment variables  
🔒 `__pycache__/` - Python cache  
🔒 `staticfiles/` - Collected static files  
🔒 `tmp/` - Temporary files  

---

## 🔄 Auto-Migration Feature

The backend includes **automatic migration** on first request after deployment:

- **Middleware**: `api.middleware.AutoMigrateMiddleware`
- **Enabled for**: Vercel (staging) and cPanel (production)
- **How it works**:
  1. On first HTTP request after deployment
  2. Checks for pending migrations
  3. Automatically runs `migrate --noinput`
  4. Logs results to application logs
  5. Continues to serve the request

### Benefits:
- ✅ No manual migration needed after deployment
- ✅ Database always up-to-date with code
- ✅ Zero downtime deployments
- ✅ Safe: runs only once per deployment

### Logs:
Check application error logs in cPanel for migration status:
```
[AUTO-MIGRATE] Database is accessible
[AUTO-MIGRATE] Found 3 pending migrations. Running them now...
[AUTO-MIGRATE] ✓ Migrations completed successfully!
[AUTO-MIGRATE] ✓ Database verified. Users: 4
```

---

## 🛠️ Troubleshooting

### Application Won't Start

1. **Check Python App Status**: Ensure it shows "Running" in cPanel
2. **Check Error Logs**: Software → Error Log
3. **Verify passenger_wsgi.py**: Should have detailed logging at startup
4. **Check Environment Variables**: Ensure all required vars are set
5. **Verify Database**: Ensure PostgreSQL is running and credentials are correct

### Migrations Not Running

1. **Manual Migration**: Run Step 5 again
2. **Check Logs**: Look for `[AUTO-MIGRATE]` messages in error logs
3. **Database Connection**: Verify DB credentials in `.env`
4. **Permissions**: Ensure database user has CREATE/ALTER permissions

### Dependencies Not Installing

1. **Check Python Version**: Ensure 3.13.5 or compatible
2. **Run Pip Install**: Click "RUN PIP INSTALL" in Python App interface
3. **Check requirements.txt**: Ensure it's present in `public_html/api/`
4. **Manual Install**: Use "Execute Python script" to install specific packages

### Static Files Not Loading

1. **Run collectstatic**: Execute Step 6 again
2. **Check .htaccess**: Ensure it's present in `public_html/api/`
3. **Verify STATIC_ROOT**: Should be `/home/zbhxqeap/public_html/api/staticfiles/`

---

## 📊 Monitoring

### Application Logs
- **Error Log**: cPanel → Software → Error Log
- **Application Output**: Shows startup messages from `passenger_wsgi.py`
- **Migration Logs**: Search for `[AUTO-MIGRATE]` prefix

### Database Status
Check database health in **Execute Python script**:
```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')
django.setup()
from api.models import User, Question, Paper
print(f"Users: {User.objects.count()}")
print(f"Questions: {Question.objects.count()}")
print(f"Papers: {Paper.objects.count()}")
```

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (50+ characters)
- [ ] Database password is secure
- [ ] `.env` file has correct permissions (600)
- [ ] CORS origins whitelist speedstarexams.co.ke only
- [ ] ALLOWED_HOSTS restricted to your domain
- [ ] SSL certificates installed and working

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [cPanel Python App Documentation](https://docs.cpanel.net/cpanel/software/python-application-manager/)
- [Passenger Documentation](https://www.phusionpassenger.com/library/)

---

**Last Updated**: December 2, 2025  
**cPanel Account**: zbhxqeap@speedstarexams.co.ke  
**Database**: zbhxqeap_exam (PostgreSQL)
