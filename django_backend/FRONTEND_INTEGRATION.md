# Frontend Integration Guide

Complete guide to connect your React frontend to the Django backend.

## 🔄 Quick Update (2 minutes)

### Step 1: Update API Base URL

**Location:** `frontend/src/services/api.js` or similar config file

**Before (Node.js):**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**After (Django):**
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### Step 2: Restart Frontend

```bash
cd frontend
npm start
```

**That's it!** Your frontend is now connected to Django! 🎉

---

## 📋 Verification Checklist

Test these features to ensure everything works:

### ✅ Authentication
- [ ] Send OTP
- [ ] Verify OTP
- [ ] Register new user
- [ ] Login existing user
- [ ] Password reset flow
- [ ] JWT token in requests
- [ ] Protected routes work

### ✅ Subject Management
- [ ] List all subjects
- [ ] Create new subject
- [ ] Create subject with papers
- [ ] Create papers with sections
- [ ] Create papers with topics
- [ ] Update subject
- [ ] Delete subject (soft)

### ✅ Question Management
- [ ] List all questions
- [ ] Filter by subject/paper/topic
- [ ] Create new question
- [ ] Create question with inline images
- [ ] Update question
- [ ] Delete question
- [ ] Search similar questions
- [ ] View statistics

---

## 🔧 Detailed Configuration

### Environment Variables

**Create/Update:** `frontend/.env`

```properties
# Django Backend
REACT_APP_API_URL=http://localhost:8000/api

# For production
# REACT_APP_API_URL=https://api.yourdomain.com/api
```

### API Service Configuration

**File:** `frontend/src/services/api.js`

```javascript
import axios from 'axios';

// API Base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle responses
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error.message);
  }
);

export default api;
```

---

## 📡 API Endpoint Reference

### Authentication Endpoints

```javascript
// Send OTP
POST /api/auth/send-otp
Body: { phoneNumber: "+254712345678", purpose: "registration" }

// Verify OTP
POST /api/auth/verify-otp
Body: { phoneNumber: "+254712345678", otp: "123456" }

// Register
POST /api/auth/register
Body: { phoneNumber: "+254712345678", fullName: "John Doe", password: "pass123" }

// Login
POST /api/auth/login
Body: { phoneNumber: "+254712345678", password: "pass123" }

// Forgot Password
POST /api/auth/forgot-password
Body: { phoneNumber: "+254712345678" }

// Reset Password
POST /api/auth/reset-password
Body: { phoneNumber: "+254712345678", otp: "123456", newPassword: "newpass123" }
```

### Subject Endpoints

```javascript
// List subjects
GET /api/subjects
GET /api/subjects?active=true

// Create subject
POST /api/subjects
Body: {
  name: "Mathematics",
  description: "Math subject",
  papers: [
    {
      name: "Paper 1",
      description: "Algebra",
      sections: ["Section A", "Section B"],
      topics: ["Algebra", "Calculus"]
    }
  ]
}

// Get subject
GET /api/subjects/{subjectId}

// Update subject
PUT /api/subjects/{subjectId}
Body: { name: "Updated Name", isActive: true }

// Delete subject
DELETE /api/subjects/{subjectId}
```

### Question Endpoints

```javascript
// List questions
GET /api/questions
GET /api/questions?subject={id}&paper={id}&topic={id}
GET /api/questions?page=1&limit=50

// Create question
POST /api/questions
Body: {
  subject: "uuid",
  paper: "uuid",
  topic: "uuid",
  section: "uuid",
  questionText: "What is 2+2?",
  answerText: "4",
  marks: 5,
  questionType: "short_answer",
  difficulty: "easy"
}

// Get question
GET /api/questions/{questionId}

// Update question
PUT /api/questions/{questionId}

// Delete question
DELETE /api/questions/{questionId}

// Search similar
GET /api/questions/search/similar?text=algebra&subject={id}

// Bulk create
POST /api/questions/bulk
Body: { questions: [...] }

// Statistics
GET /api/questions/stats/overview
```

---

## 🔐 Authentication Flow

### 1. Registration Flow

```javascript
// Step 1: Send OTP
const sendOTP = async (phoneNumber) => {
  const response = await api.post('/auth/send-otp', {
    phoneNumber,
    purpose: 'registration'
  });
  return response;
};

// Step 2: Verify OTP
const verifyOTP = async (phoneNumber, otp) => {
  const response = await api.post('/auth/verify-otp', {
    phoneNumber,
    otp
  });
  return response;
};

// Step 3: Complete Registration
const register = async (phoneNumber, fullName, password) => {
  const response = await api.post('/auth/register', {
    phoneNumber,
    fullName,
    password
  });
  
  // Save token
  localStorage.setItem('token', response.data.token);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  
  return response;
};
```

### 2. Login Flow

```javascript
const login = async (phoneNumber, password) => {
  const response = await api.post('/auth/login', {
    phoneNumber,
    password
  });
  
  // Save token and user
  localStorage.setItem('token', response.data.token);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  
  return response;
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};
```

### 3. Protected API Calls

```javascript
// Token is automatically added by interceptor
const getSubjects = async () => {
  const response = await api.get('/subjects');
  return response.data;
};

const createQuestion = async (questionData) => {
  const response = await api.post('/questions', questionData);
  return response.data;
};
```

---

## 📊 Response Format

All responses follow the same format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": {
    "field": ["Error description"]
  }
}
```

### List Response
```json
{
  "success": true,
  "message": "Items retrieved",
  "count": 10,
  "data": [
    // Array of items
  ]
}
```

---

## 🐛 Common Issues

### Issue 1: CORS Error
**Symptom:** Browser console shows CORS policy error

**Solution:**
```python
# In django_backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Issue 2: 401 Unauthorized
**Symptom:** All API calls return 401

**Solutions:**
1. Check token exists: `localStorage.getItem('token')`
2. Check token format: `Bearer <token>`
3. Token may be expired (7 days)
4. Re-login to get new token

### Issue 3: Network Error
**Symptom:** Cannot connect to API

**Solutions:**
1. Ensure Django server is running: `python manage.py runserver`
2. Check API URL is correct: `http://localhost:8000/api`
3. Check firewall settings
4. Try accessing Swagger: `http://localhost:8000/swagger/`

### Issue 4: Different Response Format
**Symptom:** Frontend expects different data structure

**Check:**
- Node.js response: `response.data.data`
- Django response: `response.data.data` (same!)
- Both return `{ success, message, data }`

---

## 🧪 Testing Integration

### Manual Testing

**Using Browser Console:**
```javascript
// Test login
fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phoneNumber: '+254712345678',
    password: 'password123'
  })
})
.then(r => r.json())
.then(console.log);

// Test protected endpoint
const token = 'your-jwt-token';
fetch('http://localhost:8000/api/subjects', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(console.log);
```

### Using Postman

Import the collection from Node.js backend and update:
1. Change base URL: `http://localhost:5000` → `http://localhost:8000`
2. All endpoints work identically

---

## 📱 Mobile App Integration

If you have React Native or mobile app:

### Update API Configuration

**Same changes:**
```javascript
// Before
const API_BASE_URL = 'http://localhost:5000/api';

// After - use your machine's IP for mobile testing
const API_BASE_URL = 'http://192.168.1.100:8000/api';
```

### Allow Host in Django

**In django_backend/.env:**
```properties
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
CORS_ALLOWED_ORIGINS=http://192.168.1.100:3000
```

---

## 🚀 Production Deployment

### Frontend Environment

**Production .env:**
```properties
REACT_APP_API_URL=https://api.yourdomain.com/api
```

### Build for Production

```bash
cd frontend
npm run build

# Deploy build folder to:
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - Any static hosting
```

### CORS Configuration

**Update django_backend/.env:**
```properties
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=api.yourdomain.com
```

---

## ✅ Integration Complete!

Your React frontend is now connected to Django backend with:
- ✅ Same API endpoints
- ✅ Same response format
- ✅ Same authentication
- ✅ Same functionality
- ✅ Better admin tools
- ✅ Auto-generated docs

**Zero breaking changes** – everything works as before! 🎉

---

## 📞 Need Help?

1. **Check Django logs:** `django_backend/django.log`
2. **Check browser console:** F12 → Console tab
3. **Check network tab:** F12 → Network tab
4. **Test in Swagger:** http://localhost:8000/swagger/
5. **Check Django admin:** http://localhost:8000/admin/

For detailed API documentation, see:
- `django_backend/README.md`
- `django_backend/QUICKSTART.md`
- Swagger UI: http://localhost:8000/swagger/
