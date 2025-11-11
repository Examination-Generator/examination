# Examination System - Complete Documentation

Welcome to the Examination System documentation. This directory contains all the essential documentation for the project.

## 📚 Documentation Index

### Getting Started
- **[Quick Start Guide](./QUICK_START.md)** - Get the project running in 5 minutes
- **[Project Overview](./PROJECT_OVERVIEW.md)** - Architecture and technology stack

### User Guides
- **[Default Users](./DEFAULT_USERS.md)** - Pre-configured admin and editor accounts
- **[Authentication](./AUTHENTICATION.md)** - Login and user management

### Developer Guides
- **[API Reference](./API_REFERENCE.md)** - Complete API endpoints documentation
- **[Database Schema](./DATABASE_SCHEMA.md)** - Database structure and models
- **[Deployment](./DEPLOYMENT.md)** - Deploy to Vercel guide

### Feature Guides
- **[Voice Transcription](./VOICE_TRANSCRIPTION.md)** - Voice-to-text input feature
- **[Text Formatting](./TEXT_FORMATTING.md)** - Rich text formatting and scientific names
- **[Edit Questions](./EDIT_QUESTIONS.md)** - Search, edit, and manage questions
- **[Subject Management](./SUBJECT_MANAGEMENT.md)** - Enhanced subject structure management

### Troubleshooting
- **[Common Issues](./TROUBLESHOOTING.md)** - Solutions to common problems

## 🚀 Quick Links

### Live Application
- **Frontend:** https://examination-frontend.vercel.app
- **Backend API:** https://examination-s3np.vercel.app
- **API Health Check:** https://examination-s3np.vercel.app/api/database/health

### Default Login Credentials
- **Admin:** Phone: `0000000001`, Password: `0000`
- **Editor:** Phone: `0000000002`, Password: `0000`

## 📂 Project Structure

```
exam/
├── frontend/exam/          # React frontend application
├── django_backend/         # Django REST API backend
├── docs/                   # All project documentation (this folder)
└── README.md              # Project overview
```

## 🛠️ Technology Stack

### Frontend
- React 18
- React Router
- Axios for API calls
- Deployed on Vercel

### Backend
- Django 5.0
- Django REST Framework
- PostgreSQL (Vercel Postgres)
- Deployed on Vercel Serverless

## 📖 Need Help?

1. Start with the [Quick Start Guide](./QUICK_START.md)
2. Check [Troubleshooting](./TROUBLESHOOTING.md) for common issues
3. Review [API Reference](./API_REFERENCE.md) for endpoint details
