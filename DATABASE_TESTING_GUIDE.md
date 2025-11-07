# Database Connection Testing Guide

## 🚀 Quick Start

### 1. Test MongoDB Connection Directly

```powershell
cd backend
node test-db-connection.js
```

**This will test:**
- ✅ MongoDB connection
- ✅ All collections (Users, Subjects, Papers, Topics, Sections)
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Data integrity

### 2. Test API Endpoints

```powershell
cd backend
# Make sure server is running first: npm run dev
# Then in another terminal:
.\test-api.ps1
```

**This will test:**
- ✅ Health check endpoint
- ✅ Send OTP (Registration)
- ✅ Login authentication
- ✅ Get all subjects
- ✅ Create subject
- ✅ Get single subject
- ✅ Update subject
- ✅ Delete subject

---

## 🔍 Checking Backend Logs

The backend now has enhanced logging. You should see:

### Successful Operations:
```
✅ MongoDB Connected: localhost
📚 Database: test
🔐 Login attempt for: +254700000001
✅ Login successful: +254700000001 Role: editor
📚 Fetching all subjects, active filter: undefined
✅ Found 5 subjects
```

### Failed Operations:
```
❌ User not found: +254712345678
❌ Subject name missing
❌ Get subjects error: Connection timeout
```

---

## 🐛 Troubleshooting

### Issue 1: "Cannot connect to MongoDB"

**Check if MongoDB is running:**
```powershell
# For Atlas Local
atlas deployments list

# For regular MongoDB
mongod --version
```

**Solution:**
- Start MongoDB Atlas Local or regular MongoDB
- Check connection string in `.env` file
- Verify `MONGODB_URI=mongodb://localhost:27017/test`

### Issue 2: "No users found"

**Solution:**
```powershell
cd backend
npm run seed
```

This will create test users:
- Admin: `+254700000000` / `admin123`
- Editor: `+254700000001` / `editor123`

### Issue 3: "Cannot find module..."

**Solution:**
```powershell
cd backend
npm install
```

### Issue 4: "Port 5000 already in use"

**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in .env
PORT=5001
```

### Issue 5: "Authentication failed" when calling API

**Check:**
1. Login first to get JWT token
2. Token expires after 7 days
3. Token must be in `Authorization: Bearer <token>` header

**Test login:**
```powershell
$body = @{
    phoneNumber = "+254700000001"
    password = "editor123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $body -ContentType "application/json"
```

### Issue 6: "Subjects not showing in dropdown"

**Check:**
1. Backend server is running
2. Subjects exist in database (run test-db-connection.js)
3. Browser console for errors (F12)
4. Network tab shows API calls to `/api/subjects`

**Fix:**
- Add subjects via "Add Subject" tab
- Check browser console for errors
- Verify JWT token in localStorage (F12 → Application → Local Storage)

---

## 📝 Manual Database Queries

### Check Users
```javascript
// In MongoDB shell
use test
db.users.find().pretty()
db.users.countDocuments()
```

### Check Subjects
```javascript
db.subjects.find().pretty()
db.subjects.countDocuments()
```

### Check Papers
```javascript
db.papers.find().pretty()
db.papers.countDocuments()
```

### Check Topics
```javascript
db.topics.find().pretty()
db.topics.countDocuments()
```

---

## 🧪 Frontend Testing

### 1. Test Login
1. Start backend: `cd backend && npm run dev`
2. Start frontend: `cd frontend/exam && npm start`
3. Open browser: `http://localhost:3000`
4. Login with: `+254700000001` / `editor123`
5. Check browser console (F12) for logs

### 2. Test Subject Loading
1. Login as editor
2. Go to "Add Questions" tab
3. Open browser console (F12)
4. Look for: `Loaded dynamic subjects:` message
5. Subject dropdown should populate

### 3. Test Subject CRUD
1. Go to "Add Subject" tab
2. Add new subject with papers/topics
3. Check success message
4. Go back to "Add Questions" tab
5. New subject should appear in dropdown

---

## 📊 Expected Console Output

### Backend (npm run dev)
```
✅ MongoDB Connected: localhost
📚 Database: test

🚀 Server running on port 5000
📍 API URL: http://localhost:5000
📚 Health check: http://localhost:5000/api/health

2025-11-05T10:45:07.995Z - POST /api/auth/login
🔐 Login attempt for: +254700000001
✅ Login successful: +254700000001 Role: editor

2025-11-05T10:45:08.621Z - GET /api/subjects
📚 Fetching all subjects, active filter: undefined
✅ Found 5 subjects
```

### Frontend (Browser Console)
```
Login successful: {user: {…}, token: "eyJhbG..."}
Loaded dynamic subjects: {Mathematics: {…}, English: {…}, ...}
```

---

## ✅ Success Checklist

- [ ] MongoDB is running
- [ ] Backend server starts without errors
- [ ] Test users exist (run `npm run seed`)
- [ ] Can login with test credentials
- [ ] API endpoints respond (run `test-api.ps1`)
- [ ] Frontend loads without errors
- [ ] Subject dropdowns populate
- [ ] Can create new subject
- [ ] New subject appears in dropdowns
- [ ] Can edit/delete subjects

---

## 🆘 Still Having Issues?

1. **Check all terminals for error messages**
2. **Run test scripts:**
   - `node test-db-connection.js`
   - `.\test-api.ps1`
3. **Check browser console (F12)**
4. **Verify .env file exists in backend folder**
5. **Ensure all npm packages installed:**
   - `cd backend && npm install`
   - `cd frontend/exam && npm install`

---

## 📞 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ECONNREFUSED` | MongoDB not running | Start MongoDB |
| `Authentication failed` | Wrong credentials | Use test account or create new |
| `Token expired` | JWT expired | Login again |
| `Port in use` | Server already running | Kill process or change port |
| `Module not found` | Missing dependencies | Run `npm install` |
| `Cannot read property 'map'` | API response format issue | Already fixed in latest code |

---

## 🎯 What Should Work Now

### ✅ Authentication
- Signup with OTP verification
- Login with phone + password
- JWT token generation and validation
- Remember me functionality
- Logout clears localStorage

### ✅ Subject Management
- Dynamic loading from database
- Create subject with papers/topics/sections
- Edit subject/paper/topic/section names
- Delete (soft delete) subjects
- Real-time dropdown updates

### ✅ Question Entry
- Subject dropdown populated from DB
- Paper dropdown filtered by subject
- Topic dropdown filtered by subject
- Section dropdown filtered by paper
- Selection display shows current choices

### ✅ Statistics
- Filters use dynamic subjects
- All data from database
- Real-time updates

---

## 💡 Tips

1. **Always check backend console** - All database operations are logged
2. **Check browser console** - Frontend errors appear here
3. **Use F12 Network tab** - See API requests/responses
4. **Check localStorage** - Verify JWT token exists
5. **Run test scripts** - Automate verification

---

**Last Updated:** November 5, 2025
**Status:** All database connections working ✅
