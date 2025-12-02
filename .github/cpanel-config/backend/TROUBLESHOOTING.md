# Backend Not Running - Troubleshooting Guide

## ❌ Problem: Directory Listing Instead of Django App

When you see "Index of /api/" with folders like `__pycache__`, `api`, `examination_system`, etc., it means the Python application is **not running**.

---

## ✅ Solution: Create Python Application in cPanel

### Step 1: Access Python App Manager

1. Login to cPanel: `https://speedstarexams.co.ke:2083`
2. Go to **Software** section
3. Click **Setup Python App**

### Step 2: Check Existing Python Apps

**If you see an existing app for `/api`:**
- Click **EDIT** on that application
- Scroll down and check the **Status** - it should say "Running"
- If it says "Stopped", click **START**
- If there are errors, click **RESTART**

**If you see NO app for `/api`:**
- Continue to Step 3 to create one

### Step 3: Create New Python Application

Click **CREATE APPLICATION** and configure:

```
Python version: 3.13.5 (or 3.12.x, 3.11.x - any version 3.9+)
Application root: api
Application URL: speedstarexams.co.ke/api
Application startup file: passenger_wsgi.py
Application Entry point: application
```

Click **CREATE**.

### Step 4: Important - Delete Auto-Generated File

⚠️ **CRITICAL**: After creating the app, cPanel auto-generates a `passenger_wsgi.py` file. This is WRONG and must be deleted.

1. Go to **File Manager**
2. Navigate to `public_html/api/`
3. Find `passenger_wsgi.py`
4. Right-click → **Delete**
5. Go back to GitHub and push code (this will deploy the correct `passenger_wsgi.py`)

### Step 5: Set Environment Variables

In the Python App interface, add these environment variables:

```bash
SECRET_KEY=django-insecure-your-random-50-char-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=speedstarexams.co.ke,www.speedstarexams.co.ke,51.91.24.182

DB_NAME=zbhxqeap_exam
DB_USER=zbhxqeap_editor
DB_PASSWORD=TesterK&700
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://speedstarexams.co.ke,https://www.speedstarexams.co.ke
```

**To generate SECRET_KEY**, use Python locally:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 6: Install Dependencies

1. In the Python App interface, scroll to **Configuration files**
2. Verify `requirements.txt` is present at `/home/zbhxqeap/public_html/api/requirements.txt`
3. Click **RUN PIP INSTALL**
4. Wait for installation to complete (may take 2-3 minutes)

### Step 7: Verify Files Exist

Go to **File Manager** → `public_html/api/` and verify these files exist:

```
✅ passenger_wsgi.py (from GitHub deployment)
✅ manage.py
✅ requirements.txt
✅ api/ (folder)
✅ examination_system/ (folder)
✅ .htaccess
```

If `passenger_wsgi.py` is missing:
- Push code from GitHub to trigger deployment
- OR manually upload from `.github/cpanel-config/backend/passenger_wsgi.py`

### Step 8: Run Initial Migration

In **Execute Python script** section of Python App, run:

```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')
django.setup()
from django.core.management import call_command
call_command('migrate', '--noinput')
print("✅ Migrations completed!")
```

### Step 9: Restart Application

Click the **RESTART** button (big red button at the top).

### Step 10: Test Backend

Visit: `https://speedstarexams.co.ke/api/`

**Expected result**: Django REST framework page or JSON response

**If you still see directory listing**:
- Check error logs: cPanel → **Metrics** → **Errors**
- Look for Python errors in the error log
- Verify Python app status is "Running"

---

## 🔍 Common Issues

### Issue 1: "Application is not running"
**Solution**: Click START or RESTART in Python App interface

### Issue 2: "No module named 'django'"
**Solution**: Click "RUN PIP INSTALL" to install requirements.txt

### Issue 3: "ImportError: cannot import name 'application'"
**Solution**: Verify `passenger_wsgi.py` exists and has correct content

### Issue 4: Database connection errors
**Solution**: 
- Verify PostgreSQL database exists: `zbhxqeap_exam`
- Check database credentials in environment variables
- Test connection in cPanel → PostgreSQL → Remote MySQL

### Issue 5: "Internal Server Error"
**Solution**: Check error logs in cPanel for detailed error message

---

## 📋 Quick Checklist

Before asking for help, verify:

- [ ] Python App created in cPanel
- [ ] Python App status = "Running"
- [ ] Environment variables set (SECRET_KEY, DB_*, etc.)
- [ ] `passenger_wsgi.py` exists in `public_html/api/`
- [ ] Dependencies installed via "RUN PIP INSTALL"
- [ ] Initial migration completed
- [ ] Application restarted
- [ ] `.htaccess` exists in `public_html/api/`

---

## 🆘 Still Not Working?

### Check Application Logs

1. Go to Python App interface
2. Scroll to **Commands** section
3. Run this in **Execute Python script**:

```python
import sys
print("Python version:", sys.version)
print("Python path:", sys.executable)
print("\nInstalled packages:")
import subprocess
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
print(result.stdout)
```

### Check Error Logs

1. cPanel → **Metrics** → **Errors**
2. Look for recent errors related to Python/Passenger
3. Copy error message and check against common issues above

### Manual Test

Upload this test file as `public_html/api/test.py`:

```python
#!/usr/bin/env python
print("Content-Type: text/html\n")
print("<h1>Python is working!</h1>")
print(f"<p>Python version: {sys.version}</p>")
```

Visit: `https://speedstarexams.co.ke/api/test.py`

If you see "Python is working!" → Python works, issue is with Django/Passenger setup  
If you see code or error → Python app not configured correctly

---

**Last Updated**: December 2, 2025
