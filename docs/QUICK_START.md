# Quick Start Guide

Get the Examination System running locally in 5 minutes.

## Prerequisites

- Python 3.9+
- Node.js 16+
- Git

## 1. Clone the Repository

```bash
git clone https://github.com/Examination-Generator/examination.git
cd exam
```

## 2. Backend Setup

```bash
cd django_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create default users
python manage.py create_default_users

# Start development server
python manage.py runserver
```

Backend will be available at: http://localhost:8000

## 3. Frontend Setup

Open a new terminal:

```bash
cd frontend/exam

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

## 4. Login

Use the default credentials:
- **Phone:** `0000000001` (Admin) or `0000000002` (Editor)
- **Password:** `0000`

## 5. Production Deployment

Both frontend and backend are automatically deployed to Vercel when you push to the `main` branch.

- **Frontend:** https://examination-frontend.vercel.app
- **Backend:** https://examination-s3np.vercel.app

## Next Steps

- Read the [Project Overview](./PROJECT_OVERVIEW.md) to understand the architecture
- Check the [API Reference](./API_REFERENCE.md) for available endpoints
- See [Default Users](./DEFAULT_USERS.md) for user management
- Review [Deployment](./DEPLOYMENT.md) for production setup

## Troubleshooting

If you encounter issues, check the [Troubleshooting Guide](./TROUBLESHOOTING.md).
