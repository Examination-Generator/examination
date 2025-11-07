# 🔧 POSTMAN TROUBLESHOOTING - Your Issues Explained

## ✅ GOOD NEWS: Backend Routes Work!

I just tested your backend directly - **ALL routes are working correctly**!

```powershell
✅ POST /api/subjects - WORKS
✅ PUT /api/subjects/:id - WORKS  
✅ DELETE /api/subjects/:id - WORKS
✅ POST /api/questions - WORKS
```

## ❌ The Problem: Postman Configuration Issues

Your Postman requests are failing due to **missing or empty environment variables**.

### Issue #1: "Route not found" for Create/Update Subject

**What's happening:**
- You're calling `/api/subjects` or `/api/subjects/{{new_subject_id}}`
- But `{{new_subject_id}}` is **EMPTY**
- So the URL becomes `/api/subjects/` (with trailing slash)
- This doesn't match any route → 404 "Route not found"

**Fix:**
1. Don't test UPDATE or DELETE until you've successfully CREATED a subject first
2. The CREATE request must succeed and save `new_subject_id` before testing UPDATE/DELETE

### Issue #2: Delete Subject showing question error

**What's happening:**
```json
{
    "message": "Subject, paper, topic, question, answer, and marks are required"
}
```

This error message is from the **CREATE QUESTION** route, not DELETE SUBJECT!

**Possible causes:**
- You accidentally selected "Create Question" instead of "Delete Subject"
- Or the URL is wrong and it's hitting `/api/questions` instead of `/api/subjects/:id`

### Issue #3: Create Question failing

**What's happening:**
The validation message tells us you're hitting the right route, but missing required fields.

**Required fields for creating a question:**
```json
{
    "subject": "MongoDB ObjectId",     // ✅ Required
    "paper": "MongoDB ObjectId",       // ✅ Required
    "topic": "MongoDB ObjectId",       // ✅ Required
    "questionText": "Question text",   // ✅ Required
    "answerText": "Answer text",       // ✅ Required
    "marks": 5                         // ✅ Required (number)
}
```

**Check:**
- Are you passing ObjectIds (not subject names)?
- Are all required fields filled?
- Is `marks` a number (not string)?

---

## 🔧 STEP-BY-STEP FIX

### Step 1: Clear All Environment Variables

In Postman:
1. Click environment dropdown (top right)
2. Select "Examination System - Development"
3. Click the eye icon
4. **DELETE or clear these values:**
   - `auth_token` → Leave EMPTY
   - `subject_id` → Leave EMPTY
   - `paper_id` → Leave EMPTY
   - `new_subject_id` → Leave EMPTY

### Step 2: Run Tests in EXACT Order

**DO NOT skip any step!**

#### ✅ 1. Login - Editor
- **Request:** `POST /api/auth/login`
- **Body:**
```json
{
    "phoneNumber": "+254700000001",
    "password": "editor123"
}
```
- **Expected:** Status 200, token saved to `{{auth_token}}`
- **Check:** Go to environment variables, confirm `auth_token` has a value

#### ✅ 2. Get All Subjects
- **Request:** `GET /api/subjects`
- **Headers:** `Authorization: Bearer {{auth_token}}`
- **Expected:** Status 200, `subject_id` saved
- **Check:** Confirm `subject_id` is now filled

#### ✅ 3. Get Subject by ID
- **Request:** `GET /api/subjects/{{subject_id}}`
- **Expected:** Status 200, `paper_id` saved
- **Check:** Confirm `paper_id` is now filled

#### ✅ 4. Create Subject
- **Request:** `POST /api/subjects`
- **Headers:** 
  - `Authorization: Bearer {{auth_token}}`
  - `Content-Type: application/json`
- **Body:**
```json
{
    "name": "Physics",
    "description": "Physics subject for secondary education",
    "papers": [
        {
            "name": "Paper 1 - Mechanics",
            "description": "Introduction to mechanics and motion",
            "sections": ["Section A", "Section B"],
            "topics": ["Mechanics", "Kinematics", "Dynamics", "Waves"]
        },
        {
            "name": "Paper 2 - Electricity",
            "description": "Electricity and magnetism",
            "sections": ["Section A"],
            "topics": ["Electricity", "Magnetism", "Electromagnetism"]
        },
        {
            "name": "Paper 3 - Practical",
            "description": "Laboratory experiments and practicals",
            "sections": ["Practical Work"],
            "topics": ["Experiments", "Data Analysis", "Lab Safety"]
        }
    ]
}
```
- **Expected:** Status 201, `new_subject_id` saved
- **Check:** Confirm `new_subject_id` is now filled in environment

#### ✅ 5. Update Subject (ONLY after step 4 succeeds!)
- **Request:** `PUT /api/subjects/{{new_subject_id}}`
- **Headers:** 
  - `Authorization: Bearer {{auth_token}}`
  - `Content-Type: application/json`
- **Body:**
```json
{
    "name": "Physics (Updated)",
    "description": "Updated description",
    "isActive": true
}
```
- **Expected:** Status 200

#### ✅ 6. Get Topics by Paper (ONLY after step 3!)
- **Request:** `GET /api/subjects/{{subject_id}}/papers/{{paper_id}}/topics`
- **Headers:** `Authorization: Bearer {{auth_token}}`
- **Expected:** Status 200

#### ✅ 7. Create Question (ONLY after step 3!)
- **Request:** `POST /api/questions`
- **Headers:**
  - `Authorization: Bearer {{auth_token}}`
  - `Content-Type: application/json`
- **Body:** (Use ObjectIds from step 3!)
```json
{
    "subject": "{{subject_id}}",
    "paper": "{{paper_id}}",
    "topic": "<topic_id_from_step3>",
    "questionText": "What is Newton's First Law?",
    "answerText": "An object at rest stays at rest.",
    "marks": 5
}
```
- **Note:** You need to manually copy a `topic._id` from step 3's response!

#### ✅ 8. Delete Subject (ONLY after step 4!)
- **Request:** `DELETE /api/subjects/{{new_subject_id}}`
- **Headers:** `Authorization: Bearer {{auth_token}}`
- **Expected:** Status 200

---

## 🎯 Common Mistakes

### ❌ Mistake 1: Running tests out of order
**Problem:** Trying to UPDATE before CREATE
**Solution:** Always CREATE first to get the ID

### ❌ Mistake 2: Empty auth token
**Problem:** Forgot to login or token expired
**Solution:** Run "Login - Editor" first, EVERY time

### ❌ Mistake 3: Wrong variable names
**Problem:** Using `{{subjectId}}` instead of `{{subject_id}}`
**Solution:** Check exact variable names in environment

### ❌ Mistake 4: Subject name already exists
**Problem:** "Physics" already exists in database
**Solution:** Change the name to "Physics 2" or delete existing one first

### ❌ Mistake 5: Using wrong HTTP method
**Problem:** Using POST when you meant PUT
**Solution:** Double-check request method dropdown

---

## 🔍 How to Debug

### Check Environment Variables
1. Click eye icon next to environment dropdown
2. Verify these have values AFTER running respective tests:
   - `auth_token` (after Login)
   - `subject_id` (after Get All Subjects)
   - `paper_id` (after Get Subject by ID)
   - `new_subject_id` (after Create Subject)

### Check Request URL
Before clicking Send:
1. Look at the URL in Postman
2. If you see `{{variable_name}}` in RED → Variable is undefined!
3. If in ORANGE → Variable is empty!
4. Should be BLACK or GREEN → Variable has value

### Check Backend Logs
Open the terminal running `npm run dev`:
```bash
📝 Creating subject: { name: 'Physics', papersCount: 3 }
✅ Subject created successfully with 3 papers
```

If you see ❌ errors, read them carefully!

---

## ✅ Verification Checklist

Before reporting an error, check:

- [ ] Backend server is running (`npm run dev`)
- [ ] MongoDB is running (Docker container)
- [ ] You ran "Login - Editor" FIRST
- [ ] `auth_token` has a value in environment
- [ ] You ran tests in the correct order
- [ ] Variable names match exactly (case-sensitive!)
- [ ] URLs don't have `{{red_variables}}`
- [ ] Request body matches the examples above
- [ ] Content-Type header is set to `application/json`

---

## 🎉 Expected Success Results

### Create Subject Success:
```json
{
    "success": true,
    "message": "Subject created successfully",
    "data": {
        "_id": "690b3397...",
        "name": "Physics",
        "papers": [...]
    }
}
```

### Update Subject Success:
```json
{
    "success": true,
    "message": "Subject updated successfully",
    "data": {
        "_id": "690b3397...",
        "name": "Physics (Updated)"
    }
}
```

### Delete Subject Success:
```json
{
    "success": true,
    "message": "Subject deleted successfully"
}
```

### Create Question Success:
```json
{
    "success": true,
    "message": "Question created successfully",
    "data": {
        "_id": "690b33a1...",
        "questionText": "What is Newton's First Law?",
        "marks": 5
    }
}
```

---

## 🆘 Still Having Issues?

1. **Export your Postman collection**
   - Click ... → Export → Save file
   - Check the actual JSON to see if URLs are correct

2. **Check network tab in Postman**
   - Look at the actual URL being called
   - Check request headers (Authorization present?)
   - Check request body (valid JSON?)

3. **Test directly with PowerShell**
   ```powershell
   # This command works - compare with your Postman request:
   $token = (Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body (@{phoneNumber="+254700000001";password="editor123"}|ConvertTo-Json) -ContentType "application/json").token
   
   $headers = @{"Authorization"="Bearer $token";"Content-Type"="application/json"}
   
   Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" -Method Post -Body (@{name="Test Physics";papers=@(@{name="Paper 1";sections=@("Section A");topics=@("Topic1")})}|ConvertTo-Json -Depth 10) -Headers $headers
   ```

---

**Remember: The backend works! The issue is with how you're calling it from Postman.** ✨
