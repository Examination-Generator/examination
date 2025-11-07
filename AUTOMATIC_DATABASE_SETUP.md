# 🚀 One-Time Automatic Database Setup

Run this **ONCE** to set up everything automatically. After this, all updates will be automatic!

## 📋 What You Need

1. **Vercel Token** - Get it here: https://vercel.com/account/tokens
   - Click "Create Token"
   - Name it: "Database Setup"
   - Scope: Full Account
   - Copy the token

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install requests
```

### Step 2: Run Automatic Setup

```bash
cd django_backend
python setup_database.py --token YOUR_VERCEL_TOKEN
```

Replace `YOUR_VERCEL_TOKEN` with the token you created.

### Step 3: That's It! ✅

The script will:
- ✅ Find your backend project automatically
- ✅ Create Vercel Postgres database (or use existing)
- ✅ Link database to project (adds POSTGRES_URL automatically)
- ✅ Set all required environment variables
- ✅ Trigger deployment with migrations

---

## 🔄 For Automatic Updates (GitHub Actions)

To make every future deployment automatic:

### Step 1: Add Secrets to GitHub

Go to: `https://github.com/Examination-Generator/examination/settings/secrets/actions`

Add these secrets:
- `VERCEL_TOKEN` - Your Vercel API token
- `VERCEL_ORG_ID` - Your Vercel team/user ID (optional)
- `VERCEL_PROJECT_ID` - Your backend project ID (optional)

### Step 2: Push Code

```bash
git add .
git commit -m "Add automatic database setup"
git push origin main
```

### Step 3: Automatic from Now On! 🎉

Every time you push code:
1. GitHub Actions runs
2. Checks if database exists
3. Creates it if missing
4. Links to project
5. Sets environment variables
6. Deploys with migrations

**You never have to think about the database again!**

---

## 🎯 What Gets Automated

| Task | Manual Before | Automatic Now |
|------|---------------|---------------|
| Create database | You had to do it | Script does it |
| Link to project | You had to do it | Script does it |
| Set POSTGRES_URL | You had to copy/paste | Auto-added |
| Set SECRET_KEY | You had to generate | Auto-generated |
| Run migrations | You had to trigger | Runs on every deploy |
| Update schema | You had to migrate | Auto-migrates on push |

---

## 📊 Verification

After running the setup:

1. **Check Home Page**
   ```
   https://examination-s3np.vercel.app/
   ```
   Should show: `"connection": "connected"`

2. **Try Login**
   Your frontend login should work without 500 errors

3. **View Logs**
   Vercel Dashboard → Deployments → Build Logs
   Should show migrations completed

---

## 🔧 Manual Commands (if needed)

### Find Your Projects
```bash
python setup_database.py --token YOUR_TOKEN --project examination
```

### Specify Region
```bash
python setup_database.py --token YOUR_TOKEN --region us-west-1
```

### For Team Accounts
```bash
python setup_database.py --token YOUR_TOKEN --team YOUR_TEAM_ID
```

---

## ❓ Troubleshooting

### "Could not find project"
Add `--project` flag with your project name:
```bash
python setup_database.py --token YOUR_TOKEN --project examination-s3np
```

### "API request failed"
- Check token is valid
- Make sure token has full access scope
- Verify you're on the correct Vercel account

### "Database already exists"
The script will ask if you want to use existing or create new. Choose option 1 to use existing.

---

## 🎉 After Setup

Once you run this setup script:

1. ✅ Database is created and linked
2. ✅ All environment variables are set
3. ✅ Deployment is triggered
4. ✅ Migrations run automatically
5. ✅ Backend is ready to use

**Future code changes:**
Just `git push` and everything updates automatically! 🚀
