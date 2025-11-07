# 🎯 Django Backend - Quick Reference Card

## 🚀 Quick Start (Copy-Paste Commands)

### Windows PowerShell
```powershell
cd django_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Linux/Mac
```bash
cd django_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| API Base | http://127.0.0.1:8000/api/ |
| Swagger Docs | http://127.0.0.1:8000/swagger/ |
| ReDoc | http://127.0.0.1:8000/redoc/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |

---

## 📡 API Endpoints Cheat Sheet

### Authentication
```
POST /api/auth/send-otp          # Send OTP
POST /api/auth/verify-otp        # Verify OTP
POST /api/auth/register          # Register user
POST /api/auth/login             # Login
POST /api/auth/forgot-password   # Forgot password
POST /api/auth/reset-password    # Reset password
```

### Subjects
```
GET    /api/subjects             # List all
POST   /api/subjects             # Create
GET    /api/subjects/{id}        # Get one
PUT    /api/subjects/{id}        # Update
DELETE /api/subjects/{id}        # Delete
```

### Questions
```
GET    /api/questions            # List all
POST   /api/questions            # Create
GET    /api/questions/{id}       # Get one
PUT    /api/questions/{id}       # Update
DELETE /api/questions/{id}       # Delete
GET    /api/questions/search/similar    # Search
POST   /api/questions/bulk       # Bulk create
GET    /api/questions/stats/overview    # Statistics
```

---

## 🔐 Authentication Header

```javascript
Authorization: Bearer <your_jwt_token>
```

---

## 📝 Request Examples

### Login
```json
POST /api/auth/login
{
  "phoneNumber": "+254712345678",
  "password": "password123"
}
```

### Create Subject
```json
POST /api/subjects
Authorization: Bearer <token>
{
  "name": "Mathematics",
  "description": "Math subject",
  "papers": [
    {
      "name": "Paper 1",
      "sections": ["Section A"],
      "topics": ["Algebra", "Calculus"]
    }
  ]
}
```

### Create Question
```json
POST /api/questions
Authorization: Bearer <token>
{
  "subject": "uuid",
  "paper": "uuid",
  "topic": "uuid",
  "questionText": "What is 2+2?",
  "answerText": "4",
  "marks": 5
}
```

---

## 📊 Response Format

### Success
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error
```json
{
  "success": false,
  "message": "Error message",
  "errors": { "field": ["error"] }
}
```

---

## 🛠️ Common Commands

### Development
```bash
python manage.py runserver          # Start server
python manage.py runserver 8080     # Custom port
python manage.py shell               # Django shell
python manage.py dbshell            # Database shell
python manage.py check              # Check for issues
```

### Database
```bash
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py showmigrations     # Show migrations
python manage.py sqlmigrate api 0001  # Show SQL
```

### Users
```bash
python manage.py createsuperuser    # Create admin
python manage.py changepassword <phone>  # Change password
```

### Static Files
```bash
python manage.py collectstatic      # Collect static files
```

---

## 🔧 Environment Variables (.env)

```properties
# Database
DB_NAME=examination_system
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=jwt-secret-key
JWT_EXPIRATION_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🐛 Quick Fixes

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Database does not exist"
```bash
psql -U postgres
CREATE DATABASE examination_system;
\q
```

### "Password authentication failed"
```
Update DB_PASSWORD in .env file
```

### "Port already in use"
```bash
python manage.py runserver 8080
```

### "Migration error"
```bash
python manage.py migrate --run-syncdb
```

---

## 📱 Frontend Integration

### Change API URL
```javascript
// Before
const API_BASE_URL = 'http://localhost:5000/api';

// After
const API_BASE_URL = 'http://localhost:8000/api';
```

### That's It!
Everything else works the same! ✅

---

## 🗄️ Database Models

```
User → Subject → Paper → Topic
                      ↓
                   Section
                      ↓
                  Question
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Complete guide |
| QUICKSTART.md | 5-min setup |
| MIGRATION_GUIDE.md | Node.js → Django |
| FRONTEND_INTEGRATION.md | Connect frontend |
| IMPLEMENTATION_SUMMARY.md | Technical details |

---

## 🎯 Default Admin Credentials

After running setup scripts:

**Phone:** +254700000000
**Password:** admin123
**Role:** admin

---

## ⚡ Production Checklist

```bash
# 1. Update .env
DEBUG=False
SECRET_KEY=new-random-key
ALLOWED_HOSTS=your-domain.com

# 2. Collect static files
python manage.py collectstatic

# 3. Use production server
pip install gunicorn
gunicorn examination_system.wsgi:application

# 4. Setup Nginx + SSL
```

---

## 🔍 Debugging

### Check Logs
```bash
tail -f django.log
```

### Enable Debug Mode
```properties
# .env
DEBUG=True
```

### Test Database Connection
```bash
python manage.py dbshell
\dt  # List tables
\q   # Quit
```

### Django Shell
```bash
python manage.py shell

>>> from api.models import User
>>> User.objects.all()
>>> exit()
```

---

## 💡 Pro Tips

1. **Use Admin Panel** for easy data management
2. **Use Swagger** for API testing
3. **Keep venv activated** while developing
4. **Run migrations** after model changes
5. **Check logs** for detailed errors
6. **Use Django shell** for debugging
7. **Test in Postman** or Swagger first

---

## 📞 Help Resources

- **Swagger UI**: Interactive API testing
- **Admin Panel**: Data management
- **django.log**: Error messages
- **README.md**: Complete documentation

---

## ✅ Success Indicators

Your setup is working if:
- ✅ Server starts without errors
- ✅ Swagger page loads
- ✅ Admin panel accessible
- ✅ Login endpoint returns token
- ✅ Frontend can connect

---

## 🎉 You're Ready!

1. Start server: `python manage.py runserver`
2. Open Swagger: http://127.0.0.1:8000/swagger/
3. Test login endpoint
4. Update frontend URL
5. Start coding!

**Happy developing!** 🚀
