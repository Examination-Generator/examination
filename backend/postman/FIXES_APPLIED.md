# 🔧 Postman Collection - Fixes Applied

## ✅ Issues Fixed

### 1. ❌ Create Subject Error
**Problem:**
```json
{
    "error": "Paper validation failed: name: Paper name is required"
}
```

**Root Cause:** The Postman request was sending nested objects:
```json
{
    "papers": [
        {
            "paperNumber": 1,
            "paperName": "Paper 1",  // ❌ Should be "name"
            "sections": [
                {
                    "sectionName": "Section A",  // ❌ Should be array of strings
                    "topics": [...]
                }
            ]
        }
    ]
}
```

**Fixed Format:** Backend expects flat arrays:
```json
{
    "name": "Physics",
    "description": "Physics subject",
    "papers": [
        {
            "name": "Paper 1 - Mechanics",  // ✅ Correct
            "description": "Intro to mechanics",
            "sections": ["Section A", "Section B"],  // ✅ Array of strings
            "topics": ["Mechanics", "Waves", "Kinematics"]  // ✅ Array of strings
        }
    ]
}
```

### 2. ❌ Get Topics by Paper Error
**Problem:**
```json
{
    "error": "Cast to ObjectId failed for value '1'"
}
```

**Root Cause:** URL was using paper number instead of paper ObjectId:
```
/api/subjects/{{subject_id}}/papers/1/topics  // ❌ "1" is not an ObjectId
```

**Fixed:** Now uses actual MongoDB ObjectId:
```
/api/subjects/{{subject_id}}/papers/{{paper_id}}/topics  // ✅ Real ObjectId
```

The `paper_id` is now auto-saved when you run "Get Subject by ID".

### 3. ❌ Update Subject Error
**Problem:** Same as #1 - wrong data structure

**Status:** ✅ Already fixed - Update endpoint just needs `name`, `description`, `isActive`

---

## 📝 Correct Request Formats

### ✅ Create Subject
```json
{
    "name": "Physics",
    "description": "Physics subject for secondary education",
    "papers": [
        {
            "name": "Paper 1 - Mechanics",
            "description": "Introduction to mechanics",
            "sections": ["Section A", "Section B"],
            "topics": ["Mechanics", "Kinematics", "Dynamics", "Waves"]
        },
        {
            "name": "Paper 2 - Electricity",
            "description": "Electricity and magnetism",
            "sections": ["Section A"],
            "topics": ["Electricity", "Magnetism", "Electromagnetism"]
        }
    ]
}
```

**Required Fields:**
- ✅ `name` - Subject name (string)
- ❌ `papers` - Optional array of paper objects

**Each Paper Object:**
- ✅ `name` - Paper name (string, required)
- ❌ `description` - Optional description
- ❌ `sections` - Optional array of section names (strings)
- ❌ `topics` - Optional array of topic names (strings)

### ✅ Update Subject
```json
{
    "name": "Physics (Updated)",
    "description": "Updated description",
    "isActive": true
}
```

**All fields optional:**
- ❌ `name` - Update subject name
- ❌ `description` - Update description
- ❌ `isActive` - Toggle active status

### ✅ Get Topics by Paper
**URL:**
```
GET /api/subjects/{{subject_id}}/papers/{{paper_id}}/topics
```

**Important:** Must use MongoDB ObjectId for `paper_id`, not paper number!

---

## 🚀 How to Use the Collection

### Step-by-Step Test Flow

#### 1. **Login First** (Required)
```
Authentication → Login - Editor → Send
```
**Result:** Token saved automatically to `{{auth_token}}`

#### 2. **Get All Subjects**
```
Subjects → Get All Subjects → Send
```
**Result:** First subject ID saved to `{{subject_id}}`

#### 3. **Get Subject Details**
```
Subjects → Get Subject by ID → Send
```
**Result:** 
- Subject details with all papers
- First paper ID saved to `{{paper_id}}`

#### 4. **Create New Subject** ✅ FIXED
```
Subjects → Create Subject → Send
```
**Result:** New subject created with 3 papers
- New subject ID saved to `{{new_subject_id}}`

#### 5. **Get Topics by Paper** ✅ FIXED
```
Subjects → Get Topics by Paper → Send
```
**Result:** All topics for the selected paper

**Note:** This now works because `{{paper_id}}` was saved in step 3!

#### 6. **Update Subject** ✅ FIXED
```
Subjects → Update Subject → Send
```
**Result:** Subject name updated

**Note:** This uses `{{new_subject_id}}` from step 4

#### 7. **Delete Subject**
```
Subjects → Delete Subject → Send
```
**Result:** Subject soft-deleted (isActive = false)

---

## 🎯 Environment Variables Auto-Saved

These variables are automatically set by the tests:

| Variable | Set By | Used By |
|----------|--------|---------|
| `auth_token` | Login - Editor | All authenticated requests |
| `user_id` | Login - Editor | Reference |
| `subject_id` | Get All Subjects | Get Subject by ID, Get Topics |
| `paper_id` | Get Subject by ID | Get Topics by Paper ✨ NEW |
| `new_subject_id` | Create Subject | Update Subject, Delete Subject |

---

## ✅ Testing Checklist

Run tests in this order:

- [ ] 1. Health Check
- [ ] 2. Login - Editor ⭐ (Required first!)
- [ ] 3. Get All Subjects
- [ ] 4. Get Subject by ID ⭐ (Saves `paper_id`)
- [ ] 5. Create Subject ✅ (Now works!)
- [ ] 6. Get Topics by Paper ✅ (Now works!)
- [ ] 7. Update Subject ✅ (Now works!)
- [ ] 8. Delete Subject

---

## 📊 Expected Results

### ✅ Create Subject Success
```json
{
    "success": true,
    "message": "Subject created successfully",
    "data": {
        "_id": "690b...",
        "name": "Physics",
        "papers": [
            {
                "_id": "690c...",
                "name": "Paper 1 - Mechanics",
                "sections": [
                    {
                        "_id": "690d...",
                        "name": "Section A"
                    }
                ],
                "topics": [
                    {
                        "_id": "690e...",
                        "name": "Mechanics"
                    }
                ]
            }
        ]
    }
}
```

### ✅ Get Topics by Paper Success
```json
{
    "success": true,
    "count": 3,
    "data": [
        {
            "_id": "690b...",
            "name": "Mechanics",
            "paper": "690c...",
            "isActive": true
        },
        {
            "_id": "690f...",
            "name": "Waves",
            "paper": "690c...",
            "isActive": true
        }
    ]
}
```

---

## 🐛 Troubleshooting

### Error: "Unauthorized"
**Solution:** Run "Login - Editor" first

### Error: "Subject not found"
**Solution:** Run "Get All Subjects" to populate `{{subject_id}}`

### Error: "Cast to ObjectId failed"
**Solution:** 
1. Run "Get Subject by ID" first (this saves `{{paper_id}}`)
2. Then run "Get Topics by Paper"

### Error: "Subject already exists"
**Solution:** Change the subject name in "Create Subject" request or delete the existing one first

### Create Subject still failing?
**Check backend logs:**
```bash
📝 Creating subject: { name: 'Physics', papersCount: 3 }
✅ Subject created successfully with 3 papers
```

If you see ❌ errors, check:
1. MongoDB is running (Docker container)
2. Backend server is running (`npm run dev`)
3. Request body matches the format above

---

## 🎓 Understanding the Data Model

```
Subject
  ├─ papers[] (array of Paper ObjectIds)
  
Paper
  ├─ name (string) ✅ Required
  ├─ subject (ObjectId reference)
  ├─ sections[] (array of Section ObjectIds)
  └─ topics[] (array of Topic ObjectIds)

Section
  ├─ name (string) ✅ Required
  └─ paper (ObjectId reference)

Topic
  ├─ name (string) ✅ Required
  └─ paper (ObjectId reference)
```

**When creating a subject:**
1. Subject document is created
2. Each paper is created with reference to subject
3. Each section is created with reference to paper
4. Each topic is created with reference to paper
5. All references are linked back

---

## 📝 Backend API Contract

### POST /api/subjects
**Expects:**
```typescript
{
    name: string (required),
    description?: string,
    papers?: Array<{
        name: string (required),
        description?: string,
        sections?: string[],  // Array of section names
        topics?: string[]     // Array of topic names
    }>
}
```

**Returns:**
```typescript
{
    success: boolean,
    message: string,
    data: Subject (with populated papers, sections, topics)
}
```

### GET /api/subjects/:subjectId/papers/:paperId/topics
**Expects:**
- `:subjectId` - MongoDB ObjectId
- `:paperId` - MongoDB ObjectId (NOT paper number!)

**Returns:**
```typescript
{
    success: boolean,
    count: number,
    data: Topic[]
}
```

---

## ✨ Summary

All Postman errors have been fixed:

✅ **Create Subject** - Now uses correct data structure  
✅ **Update Subject** - Working (just needs valid subject ID)  
✅ **Get Topics by Paper** - Now uses ObjectId instead of number  
✅ **Environment Variables** - `paper_id` now auto-saved  

**Your Postman collection is ready to use!** 🎉
