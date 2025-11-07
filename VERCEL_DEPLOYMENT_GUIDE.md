# Vercel Deployment Guide

This guide will walk you through deploying your full-stack Examination System to Vercel, including both the React frontend and Django backend with PostgreSQL database.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be pushed to GitHub
3. **Git Repository**: Push your project to GitHub

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push to GitHub**:
```bash
cd c:\Users\pc\Desktop\exam
git init
git add .
git commit -m "Initial commit - Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend (Django API)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New Project"**
3. **Import your GitHub repository**
4. **Configure Backend Deployment**:
   - **Framework Preset**: Other
   - **Root Directory**: `django_backend`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

5. **Add Environment Variables** (click "Environment Variables"):
   ```
   SECRET_KEY=your-random-secret-key-here-make-it-long-and-random
   DEBUG=False
   ALLOWED_HOSTS=.vercel.app
   JWT_SECRET_KEY=your-jwt-secret-key-here-also-random
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_DAYS=7
   DJANGO_SETTINGS_MODULE=examination_system.settings_production
   ```

6. **Click "Deploy"**
7. **Note the deployment URL** (e.g., `https://your-backend-abc123.vercel.app`)

### Step 3: Set Up Vercel Postgres Database

1. **In your backend project on Vercel**, go to the **Storage** tab
2. **Click "Create Database"**
3. **Select "Postgres"**
4. **Click "Continue"**
5. **Database will be created** and environment variables will be automatically added:
   - `POSTGRES_URL`
   - `POSTGRES_PRISMA_URL`
   - `POSTGRES_URL_NON_POOLING`
   - `POSTGRES_USER`
   - `POSTGRES_HOST`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DATABASE`

6. **Redeploy your backend** to apply the new database environment variables

### Step 4: Run Database Migrations

You need to run migrations on your Vercel Postgres database. You have two options:

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Link your project**:
```bash
cd django_backend
vercel link
```

4. **Pull environment variables**:
```bash
vercel env pull .env.production
```

5. **Run migrations locally against production database**:
```bash
python manage.py migrate --settings=examination_system.settings_production
```

#### Option B: Using psql directly

1. **Get database connection string** from Vercel dashboard (Storage > Postgres > .env.local)
2. **Connect to database**:
```bash
psql "postgres://default:PASSWORD@HOST/verceldb?sslmode=require"
```

3. **Create tables manually** or use Django management commands

### Step 5: Deploy Frontend (React App)

1. **Go back to Vercel Dashboard**
2. **Click "Add New Project"** again
3. **Select the same GitHub repository**
4. **Configure Frontend Deployment**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend/exam`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

5. **Add Environment Variables**:
   ```
   REACT_APP_API_URL=https://your-backend-abc123.vercel.app/api
   REACT_APP_ENV=production
   ```
   ⚠️ **Important**: Replace `your-backend-abc123.vercel.app` with your actual backend URL from Step 2

6. **Click "Deploy"**
7. **Note the frontend URL** (e.g., `https://your-app-xyz789.vercel.app`)

### Step 6: Update CORS Settings

1. **Go back to backend project on Vercel**
2. **Update Environment Variables**:
   - Add `CORS_ALLOWED_ORIGINS` with your frontend URL:
   ```
   CORS_ALLOWED_ORIGINS=https://your-app-xyz789.vercel.app
   ```

3. **Redeploy backend** (click "Redeploy" or push a new commit)

### Step 7: Test Your Deployment

1. **Visit your frontend URL**: `https://your-app-xyz789.vercel.app`
2. **Test registration/login**
3. **Create a test question**
4. **Check statistics**
5. **Verify data persists** (reload the page)

## 🔧 Configuration Files Created

Your project now includes these deployment files:

- `/vercel.json` - Main Vercel configuration (monorepo setup)
- `/django_backend/vercel.json` - Backend-specific configuration
- `/frontend/exam/vercel.json` - Frontend-specific configuration
- `/django_backend/examination_system/settings_production.py` - Production Django settings
- `/frontend/exam/.env.production` - Frontend production environment variables
- `/.env.production` - Example production environment variables
- `/.vercelignore` - Files to exclude from deployment

## 🗄️ Database Migration to Cloud (Future)

When you're ready to move to a cloud database (AWS RDS, Azure Database, Google Cloud SQL):

1. **Export data from Vercel Postgres**:
```bash
pg_dump "postgres://default:PASSWORD@HOST/verceldb?sslmode=require" > backup.sql
```

2. **Import to new cloud database**:
```bash
psql "your-cloud-database-url" < backup.sql
```

3. **Update environment variables** on Vercel with new database credentials:
   - `POSTGRES_HOST`
   - `POSTGRES_DATABASE`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_URL`

4. **Redeploy** your backend

## 🔐 Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (use random string generator)
- ✅ Strong `JWT_SECRET_KEY` (different from SECRET_KEY)
- ✅ CORS configured with specific allowed origins
- ✅ Database SSL enabled
- ✅ HTTPS enforced (automatic on Vercel)

## 📝 Custom Domain (Optional)

To use your own domain:

1. **Go to project settings** on Vercel
2. **Click "Domains"**
3. **Add your domain**
4. **Update DNS records** as instructed by Vercel
5. **Update CORS_ALLOWED_ORIGINS** with new domain

## 🐛 Troubleshooting

### Backend not responding
- Check Vercel function logs: Project → Deployments → Click deployment → Functions
- Verify environment variables are set correctly
- Check database connection

### Frontend can't connect to backend
- Verify `REACT_APP_API_URL` is correct
- Check CORS settings on backend
- Look at browser console for errors

### Database errors
- Verify migrations have been run
- Check database credentials
- Ensure SSL is enabled for database connections

### Static files not loading
- Run `python manage.py collectstatic` during build
- Check WhiteNoise middleware is enabled
- Verify STATIC_ROOT is configured

## 🔄 Continuous Deployment

Both deployments are now configured for automatic deployments:

- **Push to main branch** → Automatic deployment to production
- **Push to dev branch** → Can configure preview deployments
- **Pull requests** → Automatic preview deployments

## 📊 Monitoring

Monitor your deployments:

1. **Vercel Analytics**: Track page views and performance
2. **Function Logs**: Monitor API requests and errors
3. **Database Monitoring**: Check query performance in Vercel Postgres dashboard

## 💡 Tips

1. **Use environment variables** for all sensitive data
2. **Test locally** before deploying (use `.env.development`)
3. **Monitor function execution time** (Vercel has limits)
4. **Keep dependencies updated** for security
5. **Use Git tags** for version tracking
6. **Set up alerts** for deployment failures

## 🆘 Support

- **Vercel Documentation**: https://vercel.com/docs
- **Django Deployment Guide**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Vercel Community**: https://github.com/vercel/vercel/discussions

---

**Your examination system is now live on Vercel! 🎉**

Frontend: `https://your-app.vercel.app`
Backend API: `https://your-backend.vercel.app/api`
Admin Panel: `https://your-backend.vercel.app/admin`
