# Django Backend for Examination System

A complete Django REST API backend migrated from Node.js/Express with PostgreSQL database support.

## 🚀 Features

- **JWT Authentication** - Phone number based authentication with OTP verification
- **User Management** - Role-based access (User, Editor, Admin)
- **Subject Management** - Hierarchical structure (Subject → Papers → Topics/Sections)
- **Question Bank** - Full CRUD with inline images, filtering, and search
- **PostgreSQL Database** - Relational database with UUID primary keys
- **REST API** - Complete RESTful API with standardized responses
- **API Documentation** - Swagger/ReDoc documentation
- **CORS Support** - Configured for separate frontend hosting
- **Bcrypt Password Hashing** - Secure password storage
- **SMS Integration** - OTP delivery via SMS (mock/real providers)

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- virtualenv (recommended)

## 🛠️ Installation

### 1. Clone and Navigate

```bash
cd django_backend
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

**Option A: Using pgAdmin**
1. Open pgAdmin
2. Create new database: `examination_system`
3. Create user: `postgres` (or update `.env`)

**Option B: Using psql**
```bash
psql -U postgres
CREATE DATABASE examination_system;
\q
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```properties
DB_NAME=examination_system
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_EXPIRATION_DAYS=7

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts:
- Phone number: +254700000000
- Full name: Admin User
- Password: (your choice)

### 8. Run Development Server

```bash
python manage.py runserver
```

Server will start at: http://127.0.0.1:8000

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/send-otp` | Send OTP to phone number |
| POST | `/api/auth/verify-otp` | Verify OTP code |
| POST | `/api/auth/register` | Complete registration |
| POST | `/api/auth/login` | Login with credentials |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password with OTP |

### Subjects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subjects` | List all subjects |
| POST | `/api/subjects` | Create new subject |
| GET | `/api/subjects/{id}` | Get single subject |
| PUT | `/api/subjects/{id}` | Update subject |
| DELETE | `/api/subjects/{id}` | Delete subject (soft) |

### Papers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/subjects/{id}/papers` | Add paper to subject |
| GET | `/api/subjects/{subjectId}/papers/{paperId}` | Get paper details |

### Topics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/subjects/{subjectId}/papers/{paperId}/topics` | Add topic |
| GET | `/api/subjects/{subjectId}/papers/{paperId}/topics` | List topics |

### Sections

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/subjects/{subjectId}/papers/{paperId}/sections` | Add section |

### Questions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/questions` | List questions with filters |
| POST | `/api/questions` | Create question |
| GET | `/api/questions/{id}` | Get question details |
| PUT | `/api/questions/{id}` | Update question |
| DELETE | `/api/questions/{id}` | Delete question (soft) |
| GET | `/api/questions/search/similar` | Search similar questions |
| POST | `/api/questions/bulk` | Bulk create questions |
| GET | `/api/questions/stats/overview` | Get statistics |

## 🔐 Authentication

All endpoints except authentication routes require JWT token:

```bash
Authorization: Bearer <your_jwt_token>
```

### Example Login Flow

1. **Send OTP**
```bash
curl -X POST http://localhost:8000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+254712345678",
    "purpose": "registration"
  }'
```

2. **Verify OTP**
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+254712345678",
    "otp": "123456"
  }'
```

3. **Register**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+254712345678",
    "fullName": "John Doe",
    "password": "securepass123"
  }'
```

4. **Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+254712345678",
    "password": "securepass123"
  }'
```

Response includes token:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "uuid-here",
      "fullName": "John Doe",
      "phoneNumber": "+254712345678",
      "role": "user"
    }
  }
}
```

## 📖 API Documentation

Access interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

## 🗄️ Database Schema

### Tables

1. **users** - User accounts
2. **otp_logs** - OTP verification logs
3. **subjects** - Academic subjects
4. **papers** - Exam papers
5. **topics** - Topics within papers
6. **sections** - Sections within papers
7. **questions** - Question bank

All tables use UUID primary keys.

### Relationships

```
User
  ├── created_subjects (1:N)
  ├── created_papers (1:N)
  ├── created_topics (1:N)
  ├── created_sections (1:N)
  └── created_questions (1:N)

Subject
  ├── papers (1:N, CASCADE)
  └── questions (1:N, CASCADE)

Paper
  ├── topics (1:N, CASCADE)
  ├── sections (1:N, CASCADE)
  └── questions (1:N, CASCADE)

Topic
  └── questions (1:N, CASCADE)

Section
  └── questions (1:N, SET_NULL)
```

## 🔧 Management Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📁 Project Structure

```
django_backend/
├── examination_system/        # Project settings
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL config
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
├── api/                       # Main application
│   ├── migrations/           # Database migrations
│   ├── __init__.py
│   ├── admin.py              # Admin interface
│   ├── apps.py               # App configuration
│   ├── models.py             # Database models
│   ├── serializers.py        # DRF serializers
│   ├── auth_views.py         # Authentication views
│   ├── subject_views.py      # Subject management views
│   ├── question_views.py     # Question management views
│   ├── urls.py               # API URL routing
│   └── utils.py              # Utility functions
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🔄 Migration from Node.js

This Django backend is a complete rewrite of the Node.js/Express backend with feature parity:

### What's Maintained:
✅ Same API endpoints and response format
✅ JWT authentication with 7-day expiry
✅ Bcrypt password hashing
✅ Phone number authentication
✅ OTP verification flow
✅ UUID primary keys
✅ Soft delete functionality
✅ Hierarchical subject structure
✅ Question inline images support
✅ PostgreSQL database

### Key Differences:
- Python/Django instead of Node.js/Express
- Django ORM instead of Mongoose/Sequelize
- Django REST Framework instead of custom routes
- Built-in admin panel
- Better type safety with Django models
- Migration system for schema changes

### Frontend Compatibility:
The API interface is **100% compatible** with the existing React frontend. No frontend changes needed! Just update the API base URL.

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Production

1. **Update settings.py**
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

2. **Collect static files**
```bash
python manage.py collectstatic
```

3. **Use production server** (Gunicorn)
```bash
pip install gunicorn
gunicorn examination_system.wsgi:application --bind 0.0.0.0:8000
```

4. **Use Nginx as reverse proxy**

5. **Setup SSL certificate**

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check credentials in .env
# Verify database exists
psql -U postgres -l
```

### Migration Errors
```bash
# Reset migrations (development only!)
python manage.py migrate api zero
python manage.py migrate

# Or delete migrations and recreate
rm api/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

For issues, questions, or contributions:
1. Check documentation
2. Review error logs in `django.log`
3. Enable DEBUG mode for detailed errors
4. Check PostgreSQL logs

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Django REST Framework
- PostgreSQL
- Python community
