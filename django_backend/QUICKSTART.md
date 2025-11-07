# Quick Start Guide - Django Backend Setup

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Python Dependencies

```powershell
# Navigate to django_backend folder
cd django_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL

**Using pgAdmin:**
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Database name: `examination_system`
4. Owner: `postgres`
5. Click "Save"

**Or using psql:**
```bash
psql -U postgres
CREATE DATABASE examination_system;
\q
```

### Step 3: Configure Environment

The `.env` file is already created with default settings:
```properties
DB_NAME=examination_system
DB_USER=postgres
DB_PASSWORD=postgres  # ← Update this!
DB_HOST=localhost
DB_PORT=5432
```

**Update password if needed:**
1. Open `.env` in text editor
2. Change `DB_PASSWORD=postgres` to your PostgreSQL password
3. Save file

### Step 4: Initialize Database

```powershell
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
# Phone: +254700000000
# Name: Admin
# Password: admin123
```

### Step 5: Run Server

```powershell
python manage.py runserver
```

✅ **Done!** Server running at http://127.0.0.1:8000

## 🧪 Test the API

### Test Authentication

**PowerShell:**
```powershell
# Send OTP
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/send-otp" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"phoneNumber":"+254712345678","purpose":"registration"}'

# Login (if user exists)
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"phoneNumber":"+254700000000","password":"admin123"}'
```

**cURL (Git Bash):**
```bash
# Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber":"+254712345678","purpose":"registration"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber":"+254700000000","password":"admin123"}'
```

## 📱 Update Frontend

Update your React frontend API configuration:

**Before (Node.js):**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**After (Django):**
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

That's it! The API endpoints are identical, no other frontend changes needed.

## 🔧 Common Issues

### Issue: "django module not found"
**Solution:**
```powershell
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "password authentication failed"
**Solution:**
1. Open `.env` file
2. Update `DB_PASSWORD` with correct PostgreSQL password
3. Restart server

### Issue: "relation does not exist"
**Solution:**
```powershell
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Issue: "port already in use"
**Solution:**
```powershell
# Run on different port
python manage.py runserver 8080
```

## 📖 Access Documentation

- **API Docs**: http://127.0.0.1:8000/swagger/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **ReDoc**: http://127.0.0.1:8000/redoc/

## 🎯 Next Steps

1. ✅ Create some subjects via API or admin panel
2. ✅ Add papers, topics, and sections
3. ✅ Create questions
4. ✅ Test with your React frontend
5. ✅ Deploy to production

## 💡 Tips

- Use admin panel (http://127.0.0.1:8000/admin/) for easy data management
- Check `django.log` file for detailed error messages
- Use Swagger docs for API testing without Postman
- Keep virtual environment activated while developing
- Run `python manage.py check` to verify configuration

## 🚀 Production Deployment

When ready for production:

1. Update `.env`:
```properties
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=generate-new-secret-key-here
```

2. Generate new secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

3. Use Gunicorn:
```bash
pip install gunicorn
gunicorn examination_system.wsgi:application
```

4. Setup Nginx as reverse proxy

5. Use PostgreSQL on production server (not localhost)

6. Setup SSL certificate (Let's Encrypt)
