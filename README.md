"# Examination System - Full Stack Application

## 🚀 Live Demo

- **Frontend**: [Your App URL after deployment]
- **Backend API**: [Your Backend URL after deployment]
- **Admin Panel**: [Your Backend URL]/admin

## 📖 Overview

This is a full-stack examination system built with Django (backend) and React (frontend), ready for deployment on Vercel with PostgreSQL database.

### Features
- ✅ User authentication with JWT & OTP
- ✅ Question management with inline images (base64)
- ✅ Subject, Paper, Topic, and Section organization
- ✅ Similar questions search with keyword matching
- ✅ Real-time statistics dashboard
- ✅ Advanced filtering system
- ✅ Mobile responsive design

## 🛠️ Tech Stack

### Backend
- Django 5.0 + Django REST Framework
- PostgreSQL with UUID primary keys
- JWT Authentication (SimpleJWT)
- Vercel Serverless Functions compatible

### Frontend
- React 19 with Hooks
- Tailwind CSS
- Fetch API for HTTP requests

### Deployment
- Vercel (Frontend & Backend)
- Vercel Postgres (Database - can migrate to cloud later)

## 📋 Deployment Documentation

- **[📘 VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)** - Complete step-by-step deployment instructions
- **[⚡ DEPLOYMENT_QUICK_REFERENCE.md](DEPLOYMENT_QUICK_REFERENCE.md)** - Quick commands and troubleshooting
- **[✅ PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** - Ensure you're ready to deploy
- **[🗄️ DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md)** - Move database to cloud (AWS/Azure/GCP)

## 🚀 Quick Start - Local Development

### Backend Setup
```bash
cd django_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Backend runs on http://localhost:8000
```

### Frontend Setup
```bash
cd frontend/exam
npm install
npm start
# Frontend runs on http://localhost:3000
```

## 🚀 Deploy to Vercel

See **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)** for complete instructions.

---

**Ready to deploy? Start with [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)!**

*Built with ❤️ using Django & React | Deployed on Vercel* 🚀
" 
