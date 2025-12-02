# Deployment Guide

Deploy the Examination System to staging (Vercel) and production (cPanel).

## 🌐 Deployment Environments

- **Staging**: Vercel (automatic on every push)
  - Frontend: https://examination-2hhl.vercel.app
  - Backend: https://examination-s3np.vercel.app
- **Production**: cPanel (automatic 10 minutes after push)
  - Website: https://speedstarexams.co.ke
  - API: https://speedstarexams.co.ke/api

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- Vercel Postgres database
- cPanel hosting account (for production)

## 🚀 Quick Deployment

The project is configured for automatic deployment when you push to the `main` branch.

### 1. Fork/Clone Repository

```bash
git clone https://github.com/Examination-Generator/examination.git
cd exam
```

### 2. Set Up Vercel Postgres

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Storage** → **Create Database**
3. Select **Postgres**
4. Name it `examination-db`
5. Click **Create**
6. Click **Connect Project**
7. Select your examination projects (frontend and backend)
8. Click **Connect**

Vercel automatically sets the `POSTGRES_URL` environment variable.

### 3. Deploy Backend

1. Go to [Vercel Dashboard](https://vercel.com/new)
2. Import your repository
3. Select `django_backend` as the root directory
4. Set Framework Preset: **Other**
5. Set Build Command: `bash build.sh`
6. Set Output Directory: (leave empty)
7. Add Environment Variables:
   ```
   SECRET_KEY=your-secret-key-here
   DJANGO_SETTINGS_MODULE=examination_system.settings_production
   DEBUG=false
   ALLOWED_HOSTS=.vercel.app
   ```
8. Click **Deploy**

### 4. Deploy Frontend

1. Go to [Vercel Dashboard](https://vercel.com/new)
2. Import the same repository
3. Select `frontend/exam` as the root directory
4. Framework Preset: **Create React App**
5. Add Environment Variable:
   ```
   REACT_APP_API_URL=https://your-backend-url.vercel.app
   ```
6. Click **Deploy**

### 5. Verify Deployment

**Backend Health Check:**
```bash
curl https://your-backend.vercel.app/api/database/health
```

**Frontend:**
Visit your frontend URL and try logging in with:
- Phone: `0000000001`
- Password: `0000`

## 🔄 Automatic Deployments

Every push to `main` branch triggers automatic deployment to **both** staging and production:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

### Deployment Flow:

1. **Vercel Staging** (immediate):
   - ✅ Install dependencies
   - ✅ Run database migrations (auto)
   - ✅ Deploy frontend & backend
   - 🌐 Available at Vercel URLs

2. **10-Minute Wait**:
   - ⏳ Time to verify staging
   - ⏳ Rollback window if needed
   - Cancel workflow to prevent production deployment

3. **cPanel Production** (after 10 minutes):
   - ✅ Deploy frontend to public_html/
   - ✅ Deploy backend to public_html/api/
   - ✅ Auto-migration on first request
   - 🌐 Available at speedstarexams.co.ke

## 🎯 cPanel Production Setup

**First-time setup required** (one-time manual process):

See detailed guide: [`.github/cpanel-config/backend/CPANEL_SETUP_GUIDE.md`](../.github/cpanel-config/backend/CPANEL_SETUP_GUIDE.md)

### Quick Setup Steps:

1. Create Python App in cPanel (Python 3.13.5)
2. Set environment variables (SECRET_KEY, DB credentials, etc.)
3. Run `pip install` from requirements.txt
4. Run initial migration manually
5. Collect static files
6. Restart application

After this one-time setup, all future deployments are 100% automatic via GitHub Actions.

### What's Automated:

✅ Code deployment (frontend & backend)  
✅ Database migrations (auto on first request)  
✅ Dependency installation (manual trigger)  
✅ Application restart (automatic)  

### What's Preserved:

🔒 Virtual environment (venv/)  
🔒 Environment variables (.env)  
🔒 Static files (staticfiles/)  
🔒 Database data  

## 🔧 Configuration Files

### Backend: `vercel.json`
```json
{
  "builds": [
    {
      "src": "vercel_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "vercel_app.py"
    }
  ]
}
```

### Backend: `build.sh`
```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --no-input --clear || true
python manage.py migrate --noinput --settings=examination_system.settings_production
python manage.py create_default_users --settings=examination_system.settings_production || true
```

### Frontend: Standard React build
Automatically configured by Vercel for Create React App.

## 🌐 Environment Variables

### Backend (Required)
| Variable | Value | Description |
|----------|-------|-------------|
| `POSTGRES_URL` | Auto-set by Vercel | Database connection string |
| `SECRET_KEY` | Random string | Django secret key |
| `DJANGO_SETTINGS_MODULE` | `examination_system.settings_production` | Settings file |
| `DEBUG` | `false` | Debug mode |
| `ALLOWED_HOSTS` | `.vercel.app` | Allowed hosts |

### Frontend (Required)
| Variable | Value | Description |
|----------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend.vercel.app` | Backend API URL |

## 🔐 Security Checklist

Before going to production:

- [ ] Set a strong `SECRET_KEY` (min 50 characters)
- [ ] Ensure `DEBUG=false` in production
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Database connection uses `POSTGRES_URL`
- [ ] SSL/HTTPS enabled (automatic on Vercel)
- [ ] Change default user passwords
- [ ] Enable CORS only for your frontend domain

## 📊 Monitoring

### Check Deployment Status
- **Vercel Dashboard:** View real-time deployment logs
- **Health Endpoint:** `GET /api/database/health`
- **Vercel Analytics:** Built-in performance monitoring

### View Logs
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# View logs
vercel logs [deployment-url]
```

## 🐛 Troubleshooting

### Build Fails
1. Check Vercel deployment logs
2. Verify `build.sh` has execute permissions
3. Ensure all dependencies in `requirements.txt`

### Database Connection Errors
1. Verify `POSTGRES_URL` is set in Vercel
2. Check database was connected to the project
3. Run migrations: The build script does this automatically

### Default Users Not Created
1. Check build logs for `create_default_users` output
2. Manually trigger: `POST /api/database/create-defaults`
3. Verify database is accessible

### Frontend Can't Connect to Backend
1. Check `REACT_APP_API_URL` is correct
2. Verify CORS settings in backend
3. Ensure backend is deployed and accessible

## 🔄 Update Deployment

### Update Backend
```bash
cd django_backend
# Make your changes
git add .
git commit -m "Update backend"
git push origin main
```

### Update Frontend
```bash
cd frontend/exam
# Make your changes
git add .
git commit -m "Update frontend"
git push origin main
```

### Update Database Schema
1. Make model changes in `api/models.py`
2. Create migrations locally:
   ```bash
   python manage.py makemigrations
   ```
3. Commit migration files
4. Push to GitHub - migrations run automatically on deploy

## 📱 Custom Domain (Optional)

### Add Custom Domain in Vercel
1. Go to Project Settings → Domains
2. Add your domain (e.g., `exam.yourdomain.com`)
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` and `REACT_APP_API_URL`

## ✅ Post-Deployment Checklist

After successful deployment:

- [ ] Frontend loads correctly
- [ ] Can login with default credentials
- [ ] API health check returns success
- [ ] Database has 2 default users
- [ ] Can create a subject
- [ ] Can create a question
- [ ] Images upload correctly
- [ ] All pages load without errors

## 🆘 Need Help?

- Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review Vercel deployment logs
- Verify environment variables
- Test API endpoints directly
