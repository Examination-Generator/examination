# 🧪 Postman API Testing Guide

## 📋 Overview

This guide helps you test all database endpoints and verify that your MongoDB integration is working correctly with the Examination System.

## 🚀 Quick Start

### Step 1: Import into Postman

1. **Open Postman**
2. **Click "Import"** (top left)
3. **Import Collection:**
   - Drag and drop: `backend/postman/Examination_System_API.postman_collection.json`
4. **Import Environment:**
   - Drag and drop: `backend/postman/Examination_System.postman_environment.json`
5. **Select Environment:**
   - In top-right dropdown, select "Examination System - Development"

### Step 2: Run Your First Test

1. **Click on "Health & Database" → "Health Check"**
2. **Click "Send"**
3. **You should see:**
   ```json
   {
       "status": "success",
       "message": "Server is running",
       "timestamp": "2025-11-05T..."
   }
   ```

## 📚 Test Sequence (Recommended Order)

### 1️⃣ Health Check
**Purpose:** Verify server and database connection

```http
GET http://localhost:5000/api/health
```

**Expected Response:**
- ✅ Status: 200 OK
- ✅ Server running message

---

### 2️⃣ Login as Editor
**Purpose:** Get authentication token for subsequent requests

```http
POST http://localhost:5000/api/auth/login
```

**Request Body:**
```json
{
    "phoneNumber": "+254700000001",
    "password": "editor123"
}
```

**Expected Response:**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "_id": "...",
        "fullName": "Editor User",
        "phoneNumber": "+254700000001",
        "role": "editor"
    }
}
```

**Auto-Saved Variables:**
- ✅ `auth_token` - Used for all authenticated requests
- ✅ `user_id` - Current user ID
- ✅ `user_role` - Current user role

---

### 3️⃣ Get All Subjects
**Purpose:** Verify database returns all subjects

```http
GET http://localhost:5000/api/subjects
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
    "success": true,
    "data": [
        {
            "_id": "...",
            "name": "Mathematics",
            "papers": [
                {
                    "paperNumber": 1,
                    "paperName": "Paper 1",
                    "sections": [...],
                    "_id": "..."
                }
            ],
            "isActive": true,
            "createdAt": "...",
            "updatedAt": "..."
        }
    ],
    "count": 2
}
```

**Automatic Tests:**
- ✅ Response is 200 OK
- ✅ Data is an array
- ✅ Saves first subject ID for later use
- ✅ Console logs subject count

---

### 4️⃣ Get Subject by ID
**Purpose:** Test database relationships (Subject → Papers → Sections → Topics)

```http
GET http://localhost:5000/api/subjects/{{subject_id}}
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
    "success": true,
    "data": {
        "_id": "...",
        "name": "Mathematics",
        "papers": [
            {
                "paperNumber": 1,
                "paperName": "Paper 1",
                "sections": [
                    {
                        "sectionName": "Section A",
                        "topics": [
                            {
                                "topicName": "Algebra",
                                "_id": "..."
                            }
                        ],
                        "_id": "..."
                    }
                ],
                "_id": "..."
            }
        ]
    }
}
```

**Automatic Tests:**
- ✅ Subject has papers array
- ✅ Each paper has sections
- ✅ Each section has topics
- ✅ Console logs structure

---

### 5️⃣ Create New Subject
**Purpose:** Test write operations to database

```http
POST http://localhost:5000/api/subjects
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "Physics",
    "papers": [
        {
            "paperNumber": 1,
            "paperName": "Paper 1",
            "sections": [
                {
                    "sectionName": "Section A",
                    "topics": [
                        {"topicName": "Mechanics"},
                        {"topicName": "Waves"}
                    ]
                }
            ]
        },
        {
            "paperNumber": 2,
            "paperName": "Paper 2",
            "sections": [
                {
                    "sectionName": "Section A",
                    "topics": [
                        {"topicName": "Electricity"},
                        {"topicName": "Magnetism"}
                    ]
                }
            ]
        },
        {
            "paperNumber": 3,
            "paperName": "Paper 3",
            "sections": [
                {
                    "sectionName": "Practicals",
                    "topics": [
                        {"topicName": "Experiments"}
                    ]
                }
            ]
        }
    ]
}
```

**Expected Response:**
```json
{
    "success": true,
    "message": "Subject created successfully",
    "data": {
        "_id": "...",
        "name": "Physics",
        "papers": [...],
        "isActive": true
    }
}
```

**Automatic Tests:**
- ✅ Status is 201 Created
- ✅ Response has new subject ID
- ✅ Saves ID as `new_subject_id`
- ✅ Verifies papers array length

---

### 6️⃣ Get Topics by Paper
**Purpose:** Test filtered queries

```http
GET http://localhost:5000/api/subjects/{{subject_id}}/papers/1/topics
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
    "success": true,
    "data": [
        {
            "_id": "...",
            "topicName": "Algebra",
            "sectionName": "Section A"
        },
        {
            "_id": "...",
            "topicName": "Geometry",
            "sectionName": "Section A"
        }
    ]
}
```

---

### 7️⃣ Update Subject
**Purpose:** Test update operations

```http
PUT http://localhost:5000/api/subjects/{{new_subject_id}}
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "Physics (Updated)",
    "isActive": true
}
```

---

### 8️⃣ Delete Subject
**Purpose:** Test soft delete

```http
DELETE http://localhost:5000/api/subjects/{{new_subject_id}}
Authorization: Bearer {{auth_token}}
```

**Note:** This is a soft delete - sets `isActive: false`

---

## 🔍 Database Verification Tests

### Test 1: Verify Subject-Paper Relationship
**Purpose:** Ensure database relationships are intact

This test automatically:
- ✅ Checks each paper has sections
- ✅ Checks each section has topics
- ✅ Logs the structure in console
- ✅ Verifies no broken references

### Test 2: Test Dynamic Dropdown Data
**Purpose:** Verify data matches frontend requirements

This test automatically:
- ✅ Checks data structure for EditorDashboard
- ✅ Verifies all required fields exist
- ✅ Confirms dropdowns can be populated
- ✅ Logs success for each subject

---

## 🎯 What Each Test Verifies

| Test | Database Operation | Purpose |
|------|-------------------|---------|
| Health Check | Connection | MongoDB is connected |
| Login | Read (Users) | Authentication works |
| Get All Subjects | Read (Subjects) | Can fetch all records |
| Get Subject by ID | Read with populate | Relationships intact |
| Create Subject | Create | Can write to DB |
| Get Topics | Read with filter | Query filters work |
| Update Subject | Update | Can modify records |
| Delete Subject | Update (soft delete) | Can deactivate records |

---

## 📊 Automatic Test Results

Each request includes automatic tests:

### ✅ All Requests Test:
- Response time < 2000ms

### ✅ Authentication Tests:
- Status code is 200
- Token is returned
- User role is correct
- Token is auto-saved to environment

### ✅ Subject Tests:
- Status codes are correct (200, 201, etc.)
- Response has `data` property
- Data structure is valid
- Arrays are returned for lists
- Counts are logged

### ✅ Relationship Tests:
- Papers exist in subjects
- Sections exist in papers
- Topics exist in sections
- No null references

---

## 🎨 Console Output

Postman console shows:
```
✅ Token saved: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
📚 Found 2 subjects in database
✅ Sample subject: Mathematics
📄 Paper 1 has 1 sections
  📋 Section A has 3 topics
📄 Paper 2 has 1 sections
  📋 Section A has 2 topics
✅ Database relationships verified successfully
✅ Mathematics - Ready for dropdown
✅ English - Ready for dropdown
✅ Frontend can load 2 subjects into dropdown
```

---

## 🚨 Troubleshooting

### Error: "Unauthorized"
**Solution:** Run "Login - Editor" request first to get token

### Error: "ECONNREFUSED"
**Solution:** Make sure backend server is running:
```bash
cd backend
npm run dev
```

### Error: "Cannot read property 'data'"
**Solution:** Database might be empty. Run:
```bash
cd backend
npm run seed
```

### No subjects returned
**Solution:** Check MongoDB is running:
```bash
# Check connection in test-db-connection.js
node test-db-connection.js
```

---

## 🏃 Run All Tests at Once

### Option 1: Collection Runner
1. Click "Runner" (top left in Postman)
2. Drag "Examination System API" collection
3. Select "Examination System - Development" environment
4. Click "Run Examination System API"
5. View results for all 16 tests

### Option 2: CLI (Newman)
```bash
# Install Newman
npm install -g newman

# Run all tests
newman run backend/postman/Examination_System_API.postman_collection.json \
  -e backend/postman/Examination_System.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

---

## 📈 Expected Results

After running all tests, you should see:

```
┌─────────────────────────┬────────────────────┬───────────────────┐
│                         │           executed │            failed │
├─────────────────────────┼────────────────────┼───────────────────┤
│              iterations │                  1 │                 0 │
├─────────────────────────┼────────────────────┼───────────────────┤
│                requests │                 16 │                 0 │
├─────────────────────────┼────────────────────┼───────────────────┤
│            test-scripts │                 32 │                 0 │
├─────────────────────────┼────────────────────┼───────────────────┤
│      prerequest-scripts │                 16 │                 0 │
├─────────────────────────┼────────────────────┼───────────────────┤
│              assertions │                 45 │                 0 │
├─────────────────────────┴────────────────────┴───────────────────┤
│ total run duration: 2.3s                                          │
├───────────────────────────────────────────────────────────────────┤
│ total data received: 8.45kB (approx)                             │
├───────────────────────────────────────────────────────────────────┤
│ average response time: 143ms [min: 12ms, max: 456ms, s.d.: 98ms] │
└───────────────────────────────────────────────────────────────────┘
```

**✅ All tests passing = Database is working perfectly!**

---

## 🎓 Understanding the Tests

### Frontend Integration
These tests verify that:
1. **EditorDashboard dropdowns** will populate correctly
2. **Subject CRUD operations** work end-to-end
3. **Data relationships** (Subject → Paper → Section → Topic) are intact
4. **Auto-refresh** will receive updated data

### Database Verification
Each test ensures:
- MongoDB is responding
- Data is persisted correctly
- Relationships are maintained
- Queries return expected structures
- No data corruption

---

## 🔗 Next Steps

After verifying all tests pass:

1. ✅ **Open your frontend** (http://localhost:3000)
2. ✅ **Login** with editor credentials
3. ✅ **Navigate to "Add Subject"** section
4. ✅ **Verify dropdowns** load dynamically from database
5. ✅ **Create a new subject** and see it appear in dropdowns
6. ✅ **Check backend console** for emoji logs (📚 📝 ✅)

---

## 📞 Support

If any test fails:
1. Check backend console for error logs
2. Verify MongoDB Docker container is running
3. Check `.env` file has correct connection string
4. Run `node test-db-connection.js` for detailed diagnostics

**All tests passing? 🎉 Your database integration is perfect!**
