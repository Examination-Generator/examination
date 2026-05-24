"# Examination System

A full-stack web application for managing examination questions, subjects, papers, and topics. Built with Django REST Framework and React, deployed on Vercel.

## 🚀 Live Application

- **Frontend:** https://examination-frontend.vercel.app
- **Backend API:** https://examination-s3np.vercel.app/api
- **Health Check:** https://examination-s3np.vercel.app/api/database/health

## 🔑 Quick Access

**Default Login Credentials:**
- **Admin:** Phone: `0712345678`, Password: `1234`
- **Editor:** Phone: `0712345678`, Password: `1234`

## � Documentation

All documentation is located in the **[`docs/`](./docs/)** directory:

### Essential Guides
- **[Quick Start](./docs/QUICK_START.md)** - Get running in 5 minutes
- **[Project Overview](./docs/PROJECT_OVERVIEW.md)** - Architecture and tech stack
- **[Default Users](./docs/DEFAULT_USERS.md)** - Pre-configured accounts

### Reference
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Database Schema](./docs/DATABASE_SCHEMA.md)** - Database structure
- **[Authentication](./docs/AUTHENTICATION.md)** - User authentication guide

### Operations
- **[Deployment](./docs/DEPLOYMENT.md)** - Deploy to Vercel
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues & solutions

## ✨ Features

- ✅ Phone number authentication with JWT tokens
- ✅ Role-based access (User, Editor, Admin)
- ✅ Subject and paper management
- ✅ Question bank with inline images (base64)
- ✅ Topics and sections organization
- ✅ Question search and filtering
- ✅ Automatic database migrations
- ✅ Default admin/editor accounts
- ✅ Deployed on Vercel serverless

## 🛠️ Technology Stack

**Backend:**
- Django 5.0
- Django REST Framework
- PostgreSQL (Vercel Postgres)
- JWT Authentication
- Bcrypt password hashing

**Frontend:**
- React 18
- React Router v6
- Axios
- Deployed on Vercel

## � Quick Start

### Local Development

```bash
# Backend
cd django_backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py create_default_users
python manage.py runserver

# Frontend (new terminal)
cd frontend/exam
npm install
npm start
```

Visit: http://localhost:3000

### Deployment

Push to `main` branch - automatic deployment to Vercel:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

See [Deployment Guide](./docs/DEPLOYMENT.md) for details.

## 📂 Project Structure

```
exam/
├── frontend/exam/         # React frontend
├── django_backend/        # Django REST API
├── docs/                  # Complete documentation
└── README.md             # This file
```

## 🔗 Quick Links

- [📖 Full Documentation](./docs/README.md)
- [🚀 Quick Start Guide](./docs/QUICK_START.md)
- [🔐 Default Users](./docs/DEFAULT_USERS.md)
- [📡 API Reference](./docs/API_REFERENCE.md)
- [🐛 Troubleshooting](./docs/TROUBLESHOOTING.md)

## 📝 License

This project is for educational purposes.

---

**Need help?** Check the [documentation](./docs/) or [troubleshooting guide](./docs/TROUBLESHOOTING.md)." 
