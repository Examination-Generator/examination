# Database Sync: Vercel → cPanel

This guide explains how to sync all data from your Vercel Postgres database to your cPanel PostgreSQL database.

## 📋 Overview

The sync script will:
- ✅ Connect to both Vercel and cPanel databases
- ✅ Run migrations on cPanel database
- ✅ Copy all data (Users, Questions, Papers, etc.)
- ✅ Preserve IDs and relationships
- ✅ Reset auto-increment sequences

## 🚀 Quick Start

### Step 1: Get Vercel Database URL

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click **Storage** → Your Postgres Database
4. Copy the **POSTGRES_URL** connection string
   - It looks like: `postgresql://user:pass@host:5432/db`

### Step 2: Ensure cPanel .env is configured

Make sure you've created the `.env` file in `public_html/api/.env` with your cPanel database credentials:

```bash
DATABASE_URL=postgresql://your_db_user:your_db_password@localhost:5432/zbhxqeap_exam
```

### Step 3: Run the Sync Script

**On Windows (PowerShell):**
```powershell
.\scripts\sync-database.ps1 "postgresql://user:pass@host:5432/verceldb"
```

**On Linux/Mac:**
```bash
chmod +x scripts/sync-database.sh
./scripts/sync-database.sh "postgresql://user:pass@host:5432/verceldb"
```

### Step 4: Verify Sync

The script will show:
- ✅ Connection status to both databases
- 📊 Record counts for each model
- ⏳ Progress during sync
- ✅ Final summary

## 🔍 Dry Run (Preview Only)

To preview what would be synced without making changes:

**Windows:**
```powershell
.\scripts\sync-database.ps1 "postgresql://user:pass@host:5432/verceldb" --dry-run
```

**Linux/Mac:**
```bash
./scripts/sync-database.sh "postgresql://user:pass@host:5432/verceldb" --dry-run
```

## 📦 What Gets Synced

All models from the `api` app:
- 👤 Users (with authentication data)
- 📚 Subjects
- 📄 Papers
- 🔢 Topics
- ❓ Questions (with nested parts)
- 📝 Generated Papers
- 🎯 All relationships and foreign keys

## ⚠️ Important Notes

1. **One-Time Process**: This is designed to be run once to migrate your data
2. **Data Replacement**: Existing data in cPanel will be **replaced** with Vercel data
3. **Backup First**: If you have any important data in cPanel, back it up first
4. **After Sync**: Users will continue using the cPanel database (Vercel data stays separate)

## 🔧 Manual Sync (Alternative)

If you prefer to run the Django command directly:

```bash
cd django_backend

# Dry run first
python manage.py sync_vercel_to_cpanel \
  --vercel-db-url="postgresql://user:pass@host:5432/verceldb" \
  --dry-run

# Actual sync
python manage.py sync_vercel_to_cpanel \
  --vercel-db-url="postgresql://user:pass@host:5432/verceldb"
```

## 🐛 Troubleshooting

### Connection Failed

**Error:** `Connection refused` or `authentication failed`

**Solution:**
- Verify Vercel database URL is correct
- Check cPanel `.env` file has correct credentials
- Ensure both databases allow connections

### Missing Dependencies

**Error:** `No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary
```

### Foreign Key Errors

**Error:** `violates foreign key constraint`

**Solution:** The script handles dependencies automatically. If you see this error, try:
```bash
python manage.py sync_vercel_to_cpanel \
  --vercel-db-url="..." \
  --skip-migrations
```

## ✅ After Sync Complete

1. **Verify Data**: Log into your cPanel application and check that all data is present
2. **Test Functionality**: Try creating questions, generating papers, etc.
3. **Update Frontend**: Ensure frontend is pointing to cPanel backend URL
4. **GitHub Secrets**: Complete the GitHub Actions setup for automatic deployments

## 🔄 Do I Need to Sync Again?

**No!** After the initial sync:
- Users continue working with the cPanel database
- Vercel becomes your staging environment
- Production data lives on cPanel only
- No need for ongoing syncing

---

**Need Help?** Check the main deployment guide: `.github/CPANEL_DEPLOYMENT.md`
