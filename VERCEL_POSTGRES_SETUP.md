# 🗄️ Vercel Postgres Database Setup - Step by Step

## 🎯 Current Issue

Your backend is trying to connect to `localhost` because **POSTGRES_URL environment variable is NOT set on Vercel**.

Error message:
```
"connection to server at \"localhost\" (127.0.0.1), port 5432 failed: Connection refused"
```

This means: **You need to create a Vercel Postgres database and connect it to your backend.**

---

## ✅ Step-by-Step Setup (5 minutes)

### Step 1: Create Vercel Postgres Database

1. **Go to Vercel Dashboard**
   - URL: https://vercel.com/dashboard

2. **Navigate to Storage**
   - Click **"Storage"** in the top navigation menu
   - OR go to: https://vercel.com/dashboard/stores

3. **Create Postgres Database**
   - Click **"Create Database"**
   - Select **"Postgres"** (powered by Neon)
   - Choose a database name (e.g., `examination-db`)
   - Select a region (choose one close to you, e.g., `US East`)
   - Click **"Create"**

4. **Wait for Creation** (~30 seconds)
   - Vercel will provision your PostgreSQL database
   - You'll see a success message when ready

---

### Step 2: Connect Database to Your Backend Project

1. **In the Database Dashboard**
   - You should now see your database (e.g., `examination-db`)
   - Click on the database name

2. **Go to "Connect" Tab**
   - Look for **"Connect Project"** button
   - Click it

3. **Select Your Backend Project**
   - Find your backend project in the list (e.g., `examination-s3np`)
   - Select it
   - Click **"Connect"**

4. **Automatic Environment Variables** ✅
   - Vercel will **automatically** add these environment variables to your backend:
     - `POSTGRES_URL` (pooled connection - recommended)
     - `POSTGRES_URL_NON_POOLING` (direct connection)
     - `POSTGRES_PRISMA_URL` (for Prisma)
     - `POSTGRES_USER`
     - `POSTGRES_HOST`
     - `POSTGRES_PASSWORD`
     - `POSTGRES_DATABASE`

---

### Step 3: Add Missing Environment Variables

The database connection is automatic, but you still need to add these manually:

1. **Go to Your Backend Project Settings**
   - Vercel Dashboard → Your Backend Project → Settings → Environment Variables

2. **Add These Variables:**

   ```bash
   # Required
   SECRET_KEY = [Click "Generate" or use: python -c "import secrets; print(secrets.token_urlsafe(50))"]
   DJANGO_SETTINGS_MODULE = examination_system.settings_production
   
   # Optional
   DEBUG = False
   ALLOWED_HOSTS = .vercel.app
   ```

3. **How to Generate SECRET_KEY:**
   
   **Option A - Let Vercel Generate:**
   - When adding SECRET_KEY, you'll see a "Generate" button
   - Click it to create a secure random key
   
   **Option B - Generate Locally:**
   ```bash
   # In PowerShell:
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   
   Copy the output and paste as SECRET_KEY value.

---

### Step 4: Redeploy Your Backend

After connecting the database and adding environment variables:

1. **Trigger Redeployment**
   
   **Option A - Via Dashboard:**
   - Go to your backend project → Deployments
   - Click the 3 dots (...) on the latest deployment
   - Click **"Redeploy"**
   
   **Option B - Push Code:**
   ```bash
   git commit --allow-empty -m "Trigger redeploy with database"
   git push origin main
   ```

2. **Wait for Deployment** (~2-3 minutes)
   - Vercel will rebuild your backend
   - Migrations will run automatically via `build.sh`
   - Database tables will be created

---

### Step 5: Verify Database Connection

1. **Check Home Endpoint**
   
   Visit: `https://your-backend.vercel.app/`
   
   You should now see:
   ```json
   {
     "database": {
       "connection": "connected",  ✅ (was "disconnected")
       "status": "ready",
       "users_count": 0,
       "migrations_applied": true
     }
   }
   ```

2. **Check Database Health**
   
   Visit: `https://your-backend.vercel.app/api/database/health`
   
   Expected response:
   ```json
   {
     "status": "success",
     "message": "Database status: healthy",
     "data": {
       "database_connected": true,
       "tables_exist": true,
       "can_query": true,
       "migrations_needed": false
     }
   }
   ```

3. **Check Build Logs**
   
   - Vercel Dashboard → Deployments → Latest → Build Logs
   - Look for:
   ```
   ==================== RUNNING DATABASE MIGRATIONS ====================
   Running migrations:
     Applying contenttypes.0001_initial... OK
     Applying api.0001_initial... OK
   ==================== MIGRATIONS COMPLETED SUCCESSFULLY ====================
   ```

---

## 🎯 Quick Checklist

Before trying to use your backend, ensure:

- [ ] Vercel Postgres database created
- [ ] Database connected to backend project (auto-adds POSTGRES_URL)
- [ ] `SECRET_KEY` environment variable added
- [ ] `DJANGO_SETTINGS_MODULE=examination_system.settings_production` added
- [ ] Backend redeployed (automatically or manually)
- [ ] Home endpoint shows `"connection": "connected"`
- [ ] Login works without 500 errors

---

## 🚨 Troubleshooting

### Issue: "Still showing localhost error"

**Cause:** Environment variables not applied yet.

**Fix:**
1. Verify POSTGRES_URL is set: Vercel Dashboard → Backend Project → Settings → Environment Variables
2. Look for `POSTGRES_URL` - should start with `postgres://`
3. If missing, reconnect database to project (Step 2 above)
4. Redeploy after adding variables

### Issue: "Database connected but tables missing"

**Cause:** Migrations didn't run during build.

**Fix:**
```bash
# Manually trigger migrations:
curl -X POST https://your-backend.vercel.app/api/database/initialize
```

### Issue: "Build fails during migrations"

**Cause:** Database connection string incorrect or database not accessible.

**Fix:**
1. Check POSTGRES_URL format in Vercel
2. Should be: `postgres://user:pass@host:5432/db`
3. Try using `POSTGRES_URL_NON_POOLING` instead

### Issue: "Cannot create database"

**Possible causes:**
- Hobby plan limit reached (max 1 database on free tier)
- Region not available

**Fix:**
- Use existing database if you have one
- Choose different region
- Upgrade Vercel plan if needed

---

## 📊 Environment Variables Reference

After setup, you should have these in Vercel:

| Variable | Source | Required | Example Value |
|----------|--------|----------|---------------|
| `POSTGRES_URL` | Auto (from database) | ✅ | `postgres://user:pass@host/db` |
| `SECRET_KEY` | Manual | ✅ | `abc123...xyz` (50+ chars) |
| `DJANGO_SETTINGS_MODULE` | Manual | ✅ | `examination_system.settings_production` |
| `DEBUG` | Manual | ❌ | `False` |
| `ALLOWED_HOSTS` | Manual | ❌ | `.vercel.app` |
| `POSTGRES_USER` | Auto | ❌ | (from database) |
| `POSTGRES_PASSWORD` | Auto | ❌ | (from database) |

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Home endpoint shows: `"connection": "connected"`
2. ✅ `/api/database/health` returns `"healthy"`
3. ✅ Login works without errors
4. ✅ You can register new users
5. ✅ Build logs show migrations completed

---

## 🔗 Quick Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Storage/Databases:** https://vercel.com/dashboard/stores
- **Your Backend:** https://examination-s3np.vercel.app/
- **Database Health:** https://examination-s3np.vercel.app/api/database/health

---

## ⚡ TL;DR - Quick Setup

```bash
1. Vercel Dashboard → Storage → Create Postgres Database
2. Connect database to your backend project
3. Add SECRET_KEY environment variable
4. Add DJANGO_SETTINGS_MODULE=examination_system.settings_production
5. Redeploy (git push or click Redeploy)
6. Visit backend URL - should show "connected" ✅
```

**After this, your database will be fully automatic! 🚀**
