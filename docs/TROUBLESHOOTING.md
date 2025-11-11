# Troubleshooting Guide

Common issues and their solutions for the Examination System.

## 🔐 Authentication Issues

### Cannot Login with Default Credentials

**Problem:** Login fails with phone `0000000001` or `0000000002`

**Solutions:**

1. **Verify users exist:**
   ```bash
   curl https://examination-s3np.vercel.app/api/database/health
   # Check "user_count" should be 2
   ```

2. **Create default users manually:**
   ```bash
   curl -X POST https://examination-s3np.vercel.app/api/database/create-defaults
   ```

3. **Check exact password:**
   - Password is `0000` (four zeros)
   - No spaces before or after
   - Not `000` or `00000`

4. **Local development:**
   ```bash
   cd django_backend
   python manage.py create_default_users
   ```

### "Invalid credentials" Error

**Possible Causes:**
- Wrong phone number format
- Incorrect password
- User account is inactive
- Database connection issue

**Check:**
```bash
# Verify backend is running
curl https://examination-s3np.vercel.app/api/database/health

# Should return: database_connected: true
```

---

## 🗄️ Database Issues

### "Database not configured" Error

**Problem:** Backend shows database connection errors

**Solution:**

1. **Verify POSTGRES_URL is set:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Check `POSTGRES_URL` exists and has a value

2. **Reconnect database:**
   - Vercel Dashboard → Storage → Your Database
   - Click "Connect Project"
   - Select your backend project
   - Click "Connect"

3. **Check connection:**
   ```bash
   curl https://examination-s3np.vercel.app/api/database/health
   ```

### Migrations Not Running

**Problem:** Tables don't exist in database

**Solution:**

1. **Trigger manual migration:**
   ```bash
   curl -X POST https://examination-s3np.vercel.app/api/database/initialize
   ```

2. **Check build logs:**
   - Vercel Dashboard → Deployments → Latest Deployment → View Logs
   - Look for "RUNNING DATABASE MIGRATIONS"

3. **Redeploy:**
   ```bash
   git commit --allow-empty -m "Trigger rebuild"
   git push origin main
   ```

---

## 🌐 Deployment Issues

### Build Fails on Vercel

**Common Causes:**

1. **Missing dependencies:**
   - Check all packages are in `requirements.txt` (backend)
   - Check all packages are in `package.json` (frontend)

2. **Build script errors:**
   - Verify `build.sh` has correct permissions
   - Check for syntax errors in build.sh

3. **Environment variables:**
   - Ensure all required variables are set
   - Check for typos in variable names

**Check Build Logs:**
- Vercel Dashboard → Deployments → Click on deployment
- Scroll through logs to find error message

### Frontend Can't Connect to Backend

**Problem:** API requests fail or return CORS errors

**Solutions:**

1. **Update backend URL in frontend:**
   ```bash
   # In Vercel Dashboard for frontend project
   # Add environment variable:
   REACT_APP_API_URL=https://your-backend.vercel.app
   ```

2. **Check CORS settings:**
   Backend should allow your frontend domain in `settings_production.py`

3. **Verify backend is accessible:**
   ```bash
   curl https://your-backend.vercel.app/api/database/health
   ```

---

## 📁 File Upload Issues

### Images Not Uploading

**Problem:** Question/answer images fail to save

**Possible Causes:**
- Image too large (base64 bloats size)
- Invalid base64 format
- Database field limit

**Solutions:**

1. **Compress images before upload:**
   - Use smaller dimensions (max 800x600)
   - Use JPEG instead of PNG
   - Compress quality to 70-80%

2. **Verify base64 encoding:**
   ```javascript
   // Should start with: data:image/jpeg;base64,
   console.log(imageData.substring(0, 30));
   ```

3. **Check database limits:**
   - JSONB field can handle large arrays
   - But consider external storage for large files

---

## 🔄 API Issues

### 404 Not Found on API Endpoints

**Problem:** Endpoint returns 404

**Check:**

1. **Verify URL is correct:**
   ```bash
   # Correct:
   https://examination-s3np.vercel.app/api/login
   
   # Wrong:
   https://examination-s3np.vercel.app/login
   ```

2. **Check endpoint exists:**
   - See [API Reference](./API_REFERENCE.md) for all endpoints

3. **Verify method is correct:**
   - Some endpoints only accept POST
   - Some only accept GET

### 500 Internal Server Error

**Problem:** Server returns 500 error

**Debug Steps:**

1. **Check Vercel logs:**
   - Dashboard → Deployments → Functions → View logs

2. **Test locally:**
   ```bash
   cd django_backend
   python manage.py runserver
   # Try the same request
   ```

3. **Check database connection:**
   ```bash
   curl https://examination-s3np.vercel.app/api/database/health
   ```

---

## 💻 Local Development Issues

### Virtual Environment Not Activating

**Windows PowerShell:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Port Already in Use

**Problem:** `Address already in use` error

**Solution:**

**Backend (Port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Module Not Found Errors

**Problem:** `ModuleNotFoundError` when running Django

**Solution:**

1. **Ensure venv is activated:**
   - Prompt should show `(venv)`

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.9+
   ```

---

## 🎨 Frontend Issues

### Blank Page After Deployment

**Solutions:**

1. **Check browser console:**
   - F12 → Console tab
   - Look for error messages

2. **Verify build succeeded:**
   - Vercel Dashboard → Deployments
   - Check build status

3. **Clear cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Login Form Not Submitting

**Check:**

1. **Backend URL is set:**
   ```javascript
   // In your code or .env
   REACT_APP_API_URL=https://your-backend.vercel.app
   ```

2. **Network tab in browser:**
   - F12 → Network
   - Try logging in
   - Check if request is sent

3. **CORS errors:**
   - Backend must allow frontend domain

---

## 🔒 Security Issues

### "CSRF verification failed"

**Problem:** CSRF token errors

**Solution:**

For API endpoints, CSRF is typically disabled in DRF.
Check `settings_production.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### "Not authenticated" for Public Endpoints

**Problem:** Public endpoints require auth

**Check:**

Endpoints like `/api/login` should have:
```python
@permission_classes([AllowAny])
```

---

## 📊 Performance Issues

### Slow API Responses

**Possible Causes:**
- Database query optimization needed
- Too many N+1 queries
- Large image data in responses

**Solutions:**

1. **Use select_related and prefetch_related:**
   ```python
   questions = Question.objects.select_related(
       'subject', 'paper', 'topic', 'section'
   ).all()
   ```

2. **Pagination:**
   Add pagination for large lists

3. **Optimize images:**
   - Reduce image size
   - Consider external storage

---

## 🆘 Still Having Issues?

### Get More Information

1. **Check all health endpoints:**
   ```bash
   curl https://examination-s3np.vercel.app/api/database/health
   curl https://examination-s3np.vercel.app/
   ```

2. **Review deployment logs:**
   - Vercel Dashboard → Deployments → View Logs

3. **Test API directly:**
   - Use Postman or Insomnia
   - Test each endpoint individually

4. **Check documentation:**
   - [API Reference](./API_REFERENCE.md)
   - [Database Schema](./DATABASE_SCHEMA.md)
   - [Deployment Guide](./DEPLOYMENT.md)

### Common Quick Fixes

```bash
# 1. Redeploy everything
git commit --allow-empty -m "Redeploy"
git push origin main

# 2. Recreate default users
curl -X POST https://examination-s3np.vercel.app/api/database/create-defaults

# 3. Run migrations
curl -X POST https://examination-s3np.vercel.app/api/database/initialize

# 4. Check health
curl https://examination-s3np.vercel.app/api/database/health
```
