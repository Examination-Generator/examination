# Project Overview

## What is the Examination System?

The Examination System is a web application for creating, managing, and organizing educational examination questions. It supports multiple subjects, papers, topics, and sections with a powerful question bank.

## Architecture

### Frontend (React)
- **Location:** `frontend/exam/`
- **Framework:** React 18
- **Routing:** React Router v6
- **API Client:** Axios
- **Deployment:** Vercel
- **URL:** https://examination-frontend.vercel.app

### Backend (Django)
- **Location:** `django_backend/`
- **Framework:** Django 5.0 + Django REST Framework
- **Database:** PostgreSQL (Vercel Postgres)
- **Authentication:** JWT tokens with phone number login
- **Deployment:** Vercel Serverless Functions
- **URL:** https://examination-s3np.vercel.app

## Technology Stack

### Backend Technologies
```
Django 5.0.0
Django REST Framework 3.15.2
PostgreSQL (via dj-database-url)
bcrypt (password hashing)
PyJWT (token authentication)
Python 3.12
```

### Frontend Technologies
```
React 18
React Router DOM 6
Axios
CSS Modules
```

## User Roles

The system supports three user roles:

### 1. User (Regular)
- View questions
- Basic read access

### 2. Editor
- Create and edit subjects
- Create and edit papers
- Create and edit topics/sections
- Create and edit questions
- Upload images for questions/answers

### 3. Admin
- All editor permissions
- User management
- System configuration
- Full access to all features

## Database Schema

### Core Models

#### Users
- Phone number authentication (no email required)
- Password: 4-digit PIN
- Roles: user, editor, admin
- OTP verification support

#### Subjects
- Top-level organization
- Contains multiple papers
- Can be active/inactive

#### Papers
- Belongs to a subject
- Contains sections and topics
- Can be active/inactive

#### Topics
- Belongs to a paper
- Organizes questions by topic
- Can be active/inactive

#### Sections
- Belongs to a paper
- Organizes questions by exam section
- Ordered display
- Can be active/inactive

#### Questions
- Belongs to subject, paper, topic, and optionally section
- Question text with inline images (base64)
- Answer text with inline images (base64)
- Multiple question types:
  - Multiple Choice
  - True/False
  - Short Answer
  - Essay
  - Structured
- Difficulty levels: Easy, Medium, Hard
- Marks allocation
- Usage tracking
- Can be active/inactive

## Authentication Flow

### Registration (Future - requires SMS API)
1. User enters phone number and details
2. System sends OTP via SMS
3. User verifies OTP
4. User completes registration with 4-digit PIN
5. System creates account

### Current Login (Default Users)
1. User enters phone number (0000000001 or 0000000002)
2. User enters password (0000)
3. System validates and returns JWT token
4. Token used for all subsequent API calls

### Future Login (with SMS)
1. User enters phone number
2. System sends OTP
3. User enters OTP and PIN
4. System validates and returns JWT token

## API Structure

All API endpoints are prefixed with `/api/`:

```
Authentication:
- POST /api/login
- POST /api/register
- POST /api/send-otp
- POST /api/verify-otp
- POST /api/forgot-password
- POST /api/reset-password

Database Management:
- GET/POST /api/database/initialize
- GET /api/database/health
- POST /api/database/create-admin
- POST /api/database/create-defaults

Subjects:
- GET/POST /api/subjects
- GET/PUT/DELETE /api/subjects/{id}
- POST /api/subjects/{id}/papers
- GET /api/subjects/{id}/papers/{paper_id}

Topics & Sections:
- POST /api/subjects/{subject_id}/papers/{paper_id}/topics
- GET /api/subjects/{subject_id}/papers/{paper_id}/topics
- GET/PUT/DELETE /api/subjects/topics/{id}
- POST /api/subjects/{subject_id}/papers/{paper_id}/sections
- GET/PUT/DELETE /api/subjects/sections/{id}

Questions:
- GET/POST /api/questions
- GET/PUT/DELETE /api/questions/{id}
- POST /api/questions/bulk
- POST /api/questions/search-similar
- GET /api/questions/stats/overview
```

## Deployment Architecture

### Automatic Deployment
- **Trigger:** Push to `main` branch on GitHub
- **Platform:** Vercel
- **Build Process:**
  1. Install dependencies
  2. Run database migrations
  3. Create default users
  4. Deploy to serverless functions

### Environment Variables (Vercel)
```
POSTGRES_URL          # Database connection string
SECRET_KEY            # Django secret key
DJANGO_SETTINGS_MODULE # examination_system.settings_production
DEBUG                 # false
ALLOWED_HOSTS         # .vercel.app
```

## File Structure

```
exam/
├── frontend/exam/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client
│   │   └── App.js
│   ├── public/
│   └── package.json
│
├── django_backend/
│   ├── api/
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # DRF serializers
│   │   ├── urls.py         # URL routing
│   │   └── management/     # Custom commands
│   ├── examination_system/
│   │   ├── settings.py     # Local settings
│   │   ├── settings_production.py  # Production settings
│   │   └── urls.py
│   ├── manage.py
│   ├── build.sh           # Vercel build script
│   ├── vercel_app.py      # WSGI entry point
│   └── requirements.txt
│
└── docs/                  # Documentation (this folder)
```

## Default Users

The system automatically creates two default users on deployment:

### Admin User
- **Phone:** 0000000001
- **Password:** 0000
- **Role:** admin
- Full system access

### Editor User
- **Phone:** 0000000002
- **Password:** 0000
- **Role:** editor
- Can create/edit content

See [Default Users](./DEFAULT_USERS.md) for more details.

## Next Steps

- [Quick Start Guide](./QUICK_START.md) - Get started locally
- [API Reference](./API_REFERENCE.md) - Detailed API documentation
- [Database Schema](./DATABASE_SCHEMA.md) - Complete database structure
- [Deployment](./DEPLOYMENT.md) - Production deployment guide
