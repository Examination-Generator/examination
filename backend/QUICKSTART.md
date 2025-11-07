# 🚀 Quick Start Guide

## Prerequisites Checklist

- [ ] Node.js installed (v14+)
- [ ] MongoDB installed and running
- [ ] Terminal/Command Prompt open
- [ ] Code editor ready (VS Code recommended)

## Installation (5 minutes)

### Step 1: Navigate to Backend
```bash
cd c:\Users\pc\Desktop\exam\backend
```

### Step 2: Install Dependencies
```bash
npm install
```

Wait for installation to complete (~2 minutes)

### Step 3: Setup Environment
```bash
# Copy example environment file
copy .env.example .env
```

Edit `.env` file (optional - defaults work for local development):
```env
MONGODB_URI=mongodb://localhost:27017/examination_system
JWT_SECRET=your-super-secret-jwt-key
PORT=5000
```

### Step 4: Start MongoDB
```powershell
# Start MongoDB service
net start MongoDB
```

### Step 5: Seed Database with Test Data
```bash
npm run seed
```

You should see:
```
✅ MongoDB Connected
✅ Admin user created
   Phone: +254700000000
   Password: admin123
✅ Editor user created
   Phone: +254700000001
   Password: editor123
✅ Mathematics subject created
✅ English subject created
📊 DATABASE SEEDING COMPLETE
```

### Step 6: Start Server
```bash
npm run dev
```

You should see:
```
✅ MongoDB Connected: localhost
📚 Database: examination_system
🚀 Server running on port 5000
📍 API URL: http://localhost:5000
```

## Testing (2 minutes)

### Test 1: Health Check
Open browser or use curl:
```
http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "Examination System API is running",
  "timestamp": "2025-11-04T..."
}
```

### Test 2: Login
Use PowerShell or any API client:

```powershell
$body = @{
    phoneNumber = "+254700000001"
    password = "editor123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

Expected response:
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "...",
    "fullName": "Editor User",
    "phoneNumber": "+254700000001",
    "role": "editor"
  }
}
```

**Save this token!** You'll need it for authenticated requests.

### Test 3: Get Subjects
```powershell
$token = "YOUR_TOKEN_FROM_LOGIN"

Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" `
  -Method Get `
  -Headers @{ Authorization = "Bearer $token" }
```

Expected response:
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "_id": "...",
      "name": "Mathematics",
      "papers": [
        {
          "name": "Paper 1",
          "sections": [...],
          "topics": [...]
        }
      ]
    },
    {
      "_id": "...",
      "name": "English",
      "papers": [...]
    }
  ]
}
```

## 🎉 Success!

Your backend is now running and ready to accept requests from the frontend!

## Next Steps

### Connect Frontend to Backend

1. **Update Frontend Configuration**
   Create `frontend/exam/src/config.js`:
   ```javascript
   export const API_URL = 'http://localhost:5000/api';
   ```

2. **Add Authentication**
   Create `frontend/exam/src/services/auth.js`:
   ```javascript
   import { API_URL } from '../config';
   
   export const login = async (phoneNumber, password) => {
     const response = await fetch(`${API_URL}/auth/login`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ phoneNumber, password })
     });
     const data = await response.json();
     
     if (data.success) {
       localStorage.setItem('token', data.token);
       localStorage.setItem('user', JSON.stringify(data.user));
     }
     
     return data;
   };
   
   export const getToken = () => localStorage.getItem('token');
   
   export const logout = () => {
     localStorage.removeItem('token');
     localStorage.removeItem('user');
   };
   ```

3. **Load Subjects from API**
   Update `EditorDashboard.js`:
   ```javascript
   import { API_URL } from '../config';
   import { getToken } from '../services/auth';
   
   useEffect(() => {
     const loadSubjects = async () => {
       const response = await fetch(`${API_URL}/subjects`, {
         headers: { 
           'Authorization': `Bearer ${getToken()}` 
         }
       });
       const data = await response.json();
       
       if (data.success) {
         // Update state with subjects from API
         setSubjects(data.data);
       }
     };
     
     loadSubjects();
   }, []);
   ```

4. **Save Questions to API**
   Add save function:
   ```javascript
   const saveQuestion = async () => {
     const response = await fetch(`${API_URL}/questions`, {
       method: 'POST',
       headers: {
         'Authorization': `Bearer ${getToken()}`,
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({
         subject: selectedSubject._id,
         paper: selectedPaper._id,
         topic: selectedTopic._id,
         section: selectedSection?._id,
         questionText: questionText,
         questionInlineImages: questionInlineImages,
         answerText: answerText,
         answerInlineImages: answerInlineImages,
         marks: parseInt(marks)
       })
     });
     
     const data = await response.json();
     
     if (data.success) {
       alert('Question saved successfully!');
       // Clear form or navigate
     }
   };
   ```

## Common Issues & Solutions

### Issue 1: MongoDB Connection Failed
**Solution:**
```powershell
# Check if MongoDB is running
Get-Service MongoDB

# If not running, start it
net start MongoDB

# Or restart
net stop MongoDB
net start MongoDB
```

### Issue 2: Port 5000 Already in Use
**Solution:**
Change port in `.env`:
```env
PORT=5001
```

Then restart server.

### Issue 3: "npm run seed" Fails
**Solution:**
1. Make sure MongoDB is running
2. Check MongoDB connection string in `.env`
3. Clear database and try again:
   ```powershell
   # Connect to MongoDB
   mongosh
   
   # Drop database
   use examination_system
   db.dropDatabase()
   
   # Exit and run seed again
   exit
   npm run seed
   ```

### Issue 4: CORS Error from Frontend
**Solution:**
Update CORS configuration in `server.js`:
```javascript
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001'],
  credentials: true
}));
```

## API Testing Tools

### 1. Browser (for GET requests)
Simply open in browser:
```
http://localhost:5000/api/subjects
```

### 2. PowerShell (built-in)
```powershell
# GET request
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# POST request
$body = @{ key = "value" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/endpoint" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

### 3. Postman (recommended)
Download from: https://www.postman.com/downloads/

Import this collection URL:
```
http://localhost:5000/
```

### 4. VS Code REST Client Extension
Install "REST Client" extension, create `test.http`:
```http
### Login
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "phoneNumber": "+254700000001",
  "password": "editor123"
}

### Get Subjects
GET http://localhost:5000/api/subjects
Authorization: Bearer YOUR_TOKEN_HERE
```

## Development Workflow

1. **Make changes to code**
2. **Save file** (nodemon auto-restarts)
3. **Test endpoint** (Postman/PowerShell)
4. **Check logs** in terminal
5. **Repeat**

## Stopping the Server

Press `Ctrl + C` in the terminal running the server.

To stop MongoDB:
```powershell
net stop MongoDB
```

## Need Help?

1. Check the full documentation: `README.md`
2. View API flows: `SCHEMA_DIAGRAM.md`
3. Review complete guide: `DEPLOYMENT.md`
4. Check MongoDB logs: `C:\Program Files\MongoDB\Server\{version}\log\`
5. Check Node.js version: `node --version` (should be 14+)

## 📝 Test User Credentials

**Admin (Full Access):**
- Phone: `+254700000000`
- Password: `admin123`

**Editor (Question Entry):**
- Phone: `+254700000001`
- Password: `editor123`

## 🎯 You're All Set!

Your Examination System backend is now:
- ✅ Running on http://localhost:5000
- ✅ Connected to MongoDB
- ✅ Populated with test data
- ✅ Ready for frontend integration

Happy coding! 🚀
