# 🎯 SIMPLE 2-Step Database Setup

The API requires special permissions for database creation. Here's the **simplest manual + automated hybrid approach**:

---

## Step 1: Create Database (Manual - 2 minutes)

1. **Go to Vercel Dashboard**
   - https://vercel.com/dashboard/stores

2. **Click "Create Database"**
   
3. **Select "Postgres"**
   
4. **Configure:**
   - Name: `examination-db`
   - Region: `US East (1)` (or closest to you)
   
5. **Click "Create"** 
   - Wait ~30 seconds for provisioning

6. **Connect to Project:**
   - After creation, click on the database
   - Click "Connect Project" button
   - Select: `examination-s3np` (your backend)
   - Click "Connect"
   
   ✅ **This automatically adds `POSTGRES_URL` to your project!**

---

## Step 2: Set Other Variables (Automated - 30 seconds)

Now run this script to add the remaining environment variables:

```powershell
python setup_env_vars.py --token XZY0VgSXqGzx47q7EZHILuAx
```

This will:
- ✅ Find your project automatically
- ✅ Generate and set `SECRET_KEY`
- ✅ Set `DJANGO_SETTINGS_MODULE`
- ✅ Set `DEBUG=False`
- ✅ Set `ALLOWED_HOSTS`

---

## Step 3: Deploy (Automatic)

The script will tell you to either:

**Option A:** Push code
```powershell
git push origin main
```

**Option B:** Manual redeploy
- Go to Vercel Dashboard → examination-s3np → Deployments
- Click "..." on latest deployment → "Redeploy"

---

## ✅ Verification

After ~2-3 minutes, visit:
- https://examination-s3np.vercel.app/

Should show:
```json
{
  "database": {
    "connection": "connected",  ← ✅ This!
    "status": "ready"
  }
}
```

Then try login - should work! 🎉

---

## 📝 Why This Hybrid Approach?

- **Database creation** requires Vercel Dashboard (API limitations)
- **Connecting database** to project = automatic (adds POSTGRES_URL)
- **Other env vars** = script handles automatically
- **Migrations** = automatic on every deploy
- **Future updates** = 100% automatic (just push code)

**You only do Step 1 once. After that, everything is automatic!** 🚀
