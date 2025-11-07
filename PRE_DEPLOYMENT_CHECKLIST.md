# 📋 Pre-Deployment Checklist

Before deploying to Vercel, ensure you've completed all these steps:

## ✅ Code Preparation

### Backend (Django)
- [ ] All dependencies listed in `requirements.txt` with versions
- [ ] `settings_production.py` exists and is configured
- [ ] Database models are finalized
- [ ] All migrations are created (`python manage.py makemigrations`)
- [ ] Migrations have been tested locally (`python manage.py migrate`)
- [ ] Static files configuration is correct
- [ ] CORS settings are configured for production
- [ ] JWT settings are secure
- [ ] No hardcoded secrets in code
- [ ] Debug mode is controlled by environment variable
- [ ] Admin interface works
- [ ] All API endpoints tested

### Frontend (React)
- [ ] All dependencies listed in `package.json`
- [ ] Environment variables use `process.env.REACT_APP_*`
- [ ] API URLs are not hardcoded
- [ ] Build completes without errors (`npm run build`)
- [ ] No console errors in production build
- [ ] All routes work correctly
- [ ] Authentication flow works
- [ ] Mobile responsive design tested
- [ ] Error handling implemented
- [ ] Loading states implemented

## 📦 Repository Setup

- [ ] Code pushed to GitHub/GitLab/Bitbucket
- [ ] `.gitignore` excludes sensitive files
- [ ] `README.md` updated with project info
- [ ] Branch structure defined (main, dev, etc.)
- [ ] No `.env` files committed
- [ ] Large files excluded (database dumps, logs)

## 🔐 Security

- [ ] Generate strong `SECRET_KEY` for Django
- [ ] Generate strong `JWT_SECRET_KEY`
- [ ] Set `DEBUG=False` for production
- [ ] Password validators configured (if needed)
- [ ] HTTPS enforced (Vercel does this automatically)
- [ ] CORS properly configured
- [ ] SQL injection protection (Django ORM handles this)
- [ ] XSS protection enabled
- [ ] CSRF tokens disabled for API (using JWT)

## 🗄️ Database Planning

- [ ] Database schema finalized
- [ ] Understand Vercel Postgres limitations:
  - Free tier: 256 MB storage, 60 hours compute time/month
  - Paid tiers available for production use
- [ ] Have backup strategy for database
- [ ] Know how to export/import data
- [ ] Plan for future migration to cloud database
- [ ] Test migrations on a copy of production data

## 🌐 Vercel Account Setup

- [ ] Vercel account created
- [ ] GitHub account connected to Vercel
- [ ] Payment method added (if using paid features)
- [ ] Team/Organization setup (if applicable)
- [ ] Domain registered (if using custom domain)

## 📝 Environment Variables Ready

### Backend Variables
- [ ] `SECRET_KEY` generated
- [ ] `DEBUG` set to `False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] `JWT_SECRET_KEY` generated
- [ ] `JWT_ALGORITHM` set
- [ ] `JWT_EXPIRATION_DAYS` configured
- [ ] `CORS_ALLOWED_ORIGINS` prepared (will update after frontend deployment)
- [ ] `DJANGO_SETTINGS_MODULE` set to `examination_system.settings_production`

### Frontend Variables
- [ ] `REACT_APP_API_URL` prepared (will update after backend deployment)
- [ ] `REACT_APP_ENV` set to `production`

### Optional Variables
- [ ] SMS provider credentials (if using OTP)
- [ ] Email service credentials (if using email)
- [ ] Analytics keys (if using analytics)

## 🧪 Testing

### Local Testing
- [ ] Backend runs without errors
- [ ] Frontend runs without errors
- [ ] All features work end-to-end
- [ ] Database operations successful
- [ ] File uploads work (inline images)
- [ ] Authentication works
- [ ] Authorization works (user roles)

### Production-like Testing
- [ ] Test with `DEBUG=False` locally
- [ ] Test with production database settings
- [ ] Test static files serving
- [ ] Test CORS with different origins
- [ ] Performance testing done

## 📋 Deployment URLs Documented

Prepare to document these:
- [ ] Backend deployment URL
- [ ] Frontend deployment URL
- [ ] Database connection URL
- [ ] Admin panel URL

## 🔄 Deployment Strategy

- [ ] Understand deployment order (Backend → Database → Frontend)
- [ ] Have rollback plan
- [ ] Know how to view logs
- [ ] Understand how to redeploy
- [ ] CI/CD pipeline configured (optional)

## 📊 Monitoring & Maintenance

- [ ] Error tracking setup plan
- [ ] Performance monitoring plan
- [ ] Database backup schedule
- [ ] Update schedule for dependencies
- [ ] Security update plan

## 📚 Documentation

- [ ] API endpoints documented
- [ ] Environment variables documented
- [ ] Deployment process documented
- [ ] Database schema documented
- [ ] User guide created (if needed)
- [ ] Admin guide created

## 🎯 Post-Deployment Tasks

Plan to complete after deployment:
- [ ] Create admin user
- [ ] Add initial data (subjects, etc.)
- [ ] Test all features in production
- [ ] Update DNS (if using custom domain)
- [ ] Set up monitoring alerts
- [ ] Share URLs with stakeholders
- [ ] Run security audit
- [ ] Performance optimization

## ⚠️ Common Pitfalls to Avoid

- [ ] Don't commit `.env` files
- [ ] Don't use `DEBUG=True` in production
- [ ] Don't hardcode API URLs
- [ ] Don't skip database backups
- [ ] Don't use weak secret keys
- [ ] Don't ignore CORS errors
- [ ] Don't deploy without testing
- [ ] Don't forget to update CORS after frontend deployment
- [ ] Don't skip running migrations
- [ ] Don't use SQLite in production (using PostgreSQL ✓)

## 🚨 Emergency Contacts

Document these:
- [ ] Vercel support: support@vercel.com
- [ ] Database admin contact: _______
- [ ] Project lead contact: _______
- [ ] DevOps contact: _______

## 📱 Mobile Testing

- [ ] iPhone Safari tested
- [ ] Android Chrome tested
- [ ] Tablet responsive design tested
- [ ] Touch interactions work
- [ ] Forms are mobile-friendly

## 🔍 SEO & Performance (Optional)

- [ ] Meta tags added
- [ ] Open Graph tags added
- [ ] Favicon added
- [ ] Page load time optimized
- [ ] Images optimized
- [ ] Code splitting implemented

---

## ✨ Ready to Deploy?

If all checkboxes are marked, you're ready to deploy! Follow the **VERCEL_DEPLOYMENT_GUIDE.md** for step-by-step instructions.

**Good luck! 🚀**
