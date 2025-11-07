# 🎯 Quick Test Reference

## 📦 Files Created
- `Examination_System_API.postman_collection.json` - Complete API test collection
- `Examination_System.postman_environment.json` - Environment variables
- `POSTMAN_TESTING_GUIDE.md` - Detailed testing guide

## 🚀 Quick Start (3 Steps)

### 1. Import to Postman
```
1. Open Postman
2. Click "Import"
3. Drag both JSON files from backend/postman/
4. Select "Examination System - Development" environment
```

### 2. Run First Test
```
1. Click "Health & Database" → "Health Check"
2. Click "Send"
3. Should see: Status 200 OK ✅
```

### 3. Login & Test (IN ORDER!)
```
1. "Authentication" → "Login - Editor" → Send
2. Token auto-saves ✅
3. "Subjects" → "Get All Subjects" → Send (saves subject_id)
4. "Subjects" → "Get Subject by ID" → Send (saves paper_id) ⭐ IMPORTANT!
5. Now run any other test!
```

**⚠️ IMPORTANT:** Always run "Get Subject by ID" before "Get Topics by Paper"!

## 🧪 Test Categories

### 1️⃣ Health & Database (1 test)
- Health Check

### 2️⃣ Authentication (3 tests)
- Login - Editor ⭐ (Run this first!)
- Login - Admin
- Register New User

### 3️⃣ Subjects (7 tests)
- Get All Subjects ⭐
- Get Subject by ID
- Create Subject ⭐
- Update Subject
- Get Topics by Paper
- Delete Subject

### 4️⃣ Questions (2 tests)
- Get All Questions
- Create Question

### 5️⃣ Database Verification (2 tests)
- Verify Subject-Paper Relationship ⭐
- Test Dynamic Dropdown Data ⭐

**Total: 16 Tests**

## 🔑 Login Credentials

```json
Editor:
Phone: +254700000001
Password: editor123

Admin:
Phone: +254700000000
Password: admin123
```

## 📊 What Gets Tested

| ✅ | Test |
|----|------|
| ✅ | MongoDB connection working |
| ✅ | Authentication system |
| ✅ | Subject CRUD operations |
| ✅ | Database relationships intact |
| ✅ | Data structure for frontend |
| ✅ | Dynamic dropdown compatibility |
| ✅ | Response times < 2s |
| ✅ | Proper error handling |

## 🎯 Key Endpoints

```http
GET    /api/health                              # Server status
POST   /api/auth/login                          # Login
GET    /api/subjects                            # All subjects
GET    /api/subjects/:id                        # Subject details
POST   /api/subjects                            # Create subject
PUT    /api/subjects/:id                        # Update subject
DELETE /api/subjects/:id                        # Delete subject
GET    /api/subjects/:id/papers/:num/topics     # Paper topics
GET    /api/questions                           # All questions
POST   /api/questions                           # Create question
```

## 🎨 Expected Console Output

```
🧪 Running request...
✅ Token saved: eyJhbGci...
📚 Found 2 subjects in database
✅ Sample subject: Mathematics
📄 Paper 1 has 1 sections
  📋 Section A has 3 topics
✅ Database relationships verified successfully
✅ Mathematics - Ready for dropdown
✅ Frontend can load 2 subjects into dropdown
✅ Subject created: 67a1b2c3d4e5f6789
```

## 🏃 Run All Tests

### Option 1: Postman Runner
```
1. Click "Runner"
2. Select "Examination System API"
3. Click "Run"
4. See all 16 tests pass ✅
```

### Option 2: Command Line
```bash
npm install -g newman
newman run backend/postman/Examination_System_API.postman_collection.json \
  -e backend/postman/Examination_System.postman_environment.json
```

## 🚨 Common Issues

| Error | Solution |
|-------|----------|
| ECONNREFUSED | Start backend: `npm run dev` |
| Unauthorized | Run "Login - Editor" first |
| Empty data | Seed database: `npm run seed` |
| Connection failed | Check MongoDB Docker container |

## ✅ Success Checklist

- [ ] Health check returns 200 OK
- [ ] Login returns token
- [ ] Get all subjects returns array
- [ ] Subject has papers with sections and topics
- [ ] Can create new subject
- [ ] Console shows relationship verification
- [ ] All 16 tests pass

## 🎓 What This Proves

✅ **Database Integration:**
- MongoDB is connected and responding
- Data persists correctly
- Relationships are maintained

✅ **Frontend Ready:**
- EditorDashboard dropdowns will work
- Dynamic data loading works
- Auto-refresh will receive updated data

✅ **Production Ready:**
- All CRUD operations working
- Authentication functional
- Error handling in place

---

**All tests passing? 🎉 Your database is fully integrated and working!**

See `POSTMAN_TESTING_GUIDE.md` for detailed documentation.
