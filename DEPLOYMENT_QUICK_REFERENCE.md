# 🚀 Quick Deployment Commands

## Local Testing Before Deployment

### Backend (Django)
```bash
cd django_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend/exam
npm install
npm start
```

## Vercel Deployment

### 1. Initial Setup
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

### 2. Deploy Backend
```bash
cd django_backend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? exam-backend
# - Directory? ./
# - Override settings? No
```

### 3. Deploy Frontend
```bash
cd frontend/exam
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? exam-frontend
# - Directory? ./
# - Override settings? No
```

### 4. Add Environment Variables (Via Dashboard)

**Backend** (`https://vercel.com/your-account/exam-backend/settings/environment-variables`):
```
SECRET_KEY=<generate-random-string>
DEBUG=False
ALLOWED_HOSTS=.vercel.app
JWT_SECRET_KEY=<generate-random-string>
CORS_ALLOWED_ORIGINS=https://exam-frontend.vercel.app
DJANGO_SETTINGS_MODULE=examination_system.settings_production
```

**Frontend** (`https://vercel.com/your-account/exam-frontend/settings/environment-variables`):
```
REACT_APP_API_URL=https://exam-backend.vercel.app/api
REACT_APP_ENV=production
```

### 5. Set Up Database
1. Go to backend project → Storage tab
2. Create Postgres database
3. Redeploy backend to apply database variables

### 6. Run Migrations
```bash
cd django_backend
vercel env pull .env.production
python manage.py migrate --settings=examination_system.settings_production
```

## Production URLs

After deployment, you'll have:
- **Frontend**: `https://exam-frontend.vercel.app`
- **Backend API**: `https://exam-backend.vercel.app/api`
- **Admin**: `https://exam-backend.vercel.app/admin`

## Common Issues & Fixes

### Issue: "Module not found" errors
**Fix**: Make sure all dependencies are in `requirements.txt` or `package.json`

### Issue: Database connection errors
**Fix**: Ensure Vercel Postgres is created and environment variables are set

### Issue: CORS errors
**Fix**: Update `CORS_ALLOWED_ORIGINS` with your frontend URL and redeploy backend

### Issue: Static files not loading
**Fix**: Run `python manage.py collectstatic --no-input` in build command

### Issue: Frontend shows blank page
**Fix**: Check browser console, verify `REACT_APP_API_URL` is correct

## Redeploy Commands

### Redeploy Backend
```bash
cd django_backend
vercel --prod
```

### Redeploy Frontend
```bash
cd frontend/exam
vercel --prod
```

## Environment Variables Quick Reference

### Generate Secret Keys
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Or use online generator
# https://djecrety.ir/
```

### Required Backend Variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Should be `False` in production
- `ALLOWED_HOSTS` - `.vercel.app` or your domain
- `JWT_SECRET_KEY` - JWT signing key
- `CORS_ALLOWED_ORIGINS` - Frontend URL
- `DJANGO_SETTINGS_MODULE` - `examination_system.settings_production`

### Required Frontend Variables
- `REACT_APP_API_URL` - Backend API URL (must start with REACT_APP_)
- `REACT_APP_ENV` - `production`

### Database Variables (Auto-added by Vercel Postgres)
- `POSTGRES_URL`
- `POSTGRES_USER`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

## Testing Checklist

After deployment, test these features:

- [ ] User Registration (OTP flow)
- [ ] User Login
- [ ] Create Subject
- [ ] Create Question with inline images
- [ ] View Statistics
- [ ] Search Similar Questions
- [ ] Filter Questions
- [ ] Data persists after page reload
- [ ] Mobile responsiveness

## Monitoring

### View Logs
```bash
# Backend logs
vercel logs exam-backend

# Frontend logs
vercel logs exam-frontend
```

### Real-time logs
```bash
vercel logs --follow
```

## Rollback

If something goes wrong:

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote <deployment-url>
```

## Custom Domain Setup

1. Go to project settings → Domains
2. Add your domain (e.g., `exam.yourdomain.com`)
3. Update DNS with provided records
4. Update environment variables with new domain
5. Redeploy

---

**Need help?** Check `VERCEL_DEPLOYMENT_GUIDE.md` for detailed instructions.
