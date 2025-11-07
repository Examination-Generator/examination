# Examination System - Phase 1 Complete Package

## 🎯 Overview

Complete MongoDB backend implementation for an Examination System with:
- ✅ Phone number authentication with OTP
- ✅ Hierarchical subject/paper/topic/section structure
- ✅ Rich question bank with inline images
- ✅ RESTful API endpoints
- ✅ JWT authentication
- ✅ Role-based access control

## 📁 Project Structure

```
exam/
├── frontend/
│   └── exam/
│       └── src/
│           └── components/
│               └── EditorDashboard.js  (React editor with image support)
│
└── backend/                            ⭐ NEW
    ├── config/
    │   └── database.js                 Database connection config
    │
    ├── middleware/
    │   └── auth.js                     JWT authentication middleware
    │
    ├── models/
    │   └── schema.js                   All MongoDB schemas
    │
    ├── routes/
    │   ├── auth.js                     Authentication endpoints
    │   ├── subjects.js                 Subject management endpoints
    │   └── questions.js                Question management endpoints
    │
    ├── scripts/
    │   └── seedDatabase.js             Database seeding script
    │
    ├── .env.example                    Environment variables template
    ├── .gitignore                      Git ignore rules
    ├── package.json                    Dependencies
    ├── server.js                       Main server file
    ├── README.md                       Complete documentation
    └── SCHEMA_DIAGRAM.md               Visual schema diagrams
```

## 🗄️ Database Schema

### Collections Created

1. **users** - User authentication and profiles
   - Phone number registration
   - OTP verification
   - Password management
   - Role-based access (admin/editor/viewer)

2. **subjects** - Root level subjects
   - Name, description
   - References to papers
   - Active/inactive status

3. **papers** - Papers within subjects
   - Belongs to subject
   - Contains sections (0 or more)
   - Contains topics
   - Papers can have NO sections (sections array can be empty)

4. **sections** - Optional sections within papers
   - Belongs to paper
   - Ordered sections (Section A, B, C, etc.)
   - Not all papers need sections

5. **topics** - Topics within papers
   - Belongs to paper
   - Can optionally belong to section
   - **Topics are filtered by paper** (critical requirement)

6. **questions** - Question bank
   - Classified by: subject → paper → topic → section (optional)
   - Rich content support:
     - Question text with image placeholders
     - Answer text with image placeholders
     - Inline images array (base64 encoded)
     - Image metadata (id, url, width, height, type)
   - Marks allocation
   - Usage tracking

7. **otplogs** - OTP verification tracking
   - Phone number
   - OTP code
   - Purpose (registration/login/password_reset)
   - Status and expiration
   - Security tracking

8. **sessions** - User session management
   - JWT token tracking
   - IP address and user agent
   - Automatic expiration

## 🔐 Authentication Flow

### 1. Registration
```
User enters phone → Send OTP → Verify OTP → Set password → Receive JWT token
```

### 2. Login
```
User enters phone + password → Verify credentials → Receive JWT token
```

### 3. Password Reset
```
User enters phone → Send OTP → Verify OTP → Set new password → Success
```

## 🏗️ Hierarchical Structure (Critical Concept)

```
Subject (e.g., Mathematics)
  └── Paper (e.g., Paper 1, Paper 2, Paper 3)
       ├── Section (0 or more - e.g., Section A, Section B)
       │    └── Topics can be assigned to specific sections
       │
       └── Topic (filtered by paper - e.g., Algebra, Calculus)
            └── Questions are classified here
```

### Key Points:
- ✅ Topics are **filtered by paper** (not all papers share same topics)
- ✅ Papers can have **0 or more sections** (some papers have none)
- ✅ Topics can optionally belong to a specific section
- ✅ Questions must reference: subject, paper, topic, and optionally section

## 🎨 Image Support (From Editor)

The frontend EditorDashboard supports:

1. **Image Upload** - User uploads files
2. **Drawing Tool** - Canvas-based drawing
3. **Graph Paper** - 10px grid for diagrams

All images are:
- Converted to base64
- Stored with metadata (id, width, height, type)
- Inserted as placeholders: `[IMAGE:id:300x200px]`
- Rendered as actual images in rich content display

## 📡 API Endpoints Summary

### Authentication (`/api/auth`)
- POST `/send-otp` - Send OTP to phone
- POST `/verify-otp` - Verify OTP code
- POST `/register` - Complete registration
- POST `/login` - Login with credentials
- POST `/forgot-password` - Initiate password reset
- POST `/reset-password` - Complete password reset

### Subjects (`/api/subjects`)
- POST `/` - Create subject with papers/sections/topics
- GET `/` - Get all subjects
- GET `/:id` - Get single subject
- PUT `/:id` - Update subject
- DELETE `/:id` - Soft delete subject
- POST `/:id/papers` - Add paper to subject
- POST `/:subjectId/papers/:paperId/sections` - Add section to paper
- POST `/:subjectId/papers/:paperId/topics` - Add topic to paper
- GET `/:subjectId/papers/:paperId/topics` - **Get topics filtered by paper**

### Questions (`/api/questions`)
- POST `/` - Create question with images
- GET `/` - Get questions with filters
- GET `/:id` - Get single question
- PUT `/:id` - Update question
- DELETE `/:id` - Soft delete question
- GET `/search/similar` - Search similar questions
- POST `/bulk` - Create multiple questions
- GET `/stats/overview` - Get statistics

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your MongoDB URI and JWT secret
```

### 3. Start MongoDB
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### 4. Seed Database (Optional)
```bash
npm run seed
```

This creates:
- Admin user: `+254700000000` / `admin123`
- Editor user: `+254700000001` / `editor123`
- Sample subjects (Mathematics, English)
- Sample papers with sections and topics
- Sample questions

### 5. Start Server
```bash
# Development mode
npm run dev

# Production mode
npm start
```

Server runs on: `http://localhost:5000`

## 🧪 Testing the API

### Test Authentication
```bash
# 1. Login (using seeded user)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+254700000001", "password": "editor123"}'

# Response includes token:
# { "success": true, "token": "eyJhbGc..." }
```

### Test Subject Management
```bash
# 2. Get all subjects (use token from login)
curl http://localhost:5000/api/subjects \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. Get topics for a specific paper
curl "http://localhost:5000/api/subjects/SUBJECT_ID/papers/PAPER_ID/topics" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Question Creation
```bash
# 4. Create question
curl -X POST http://localhost:5000/api/questions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "SUBJECT_ID",
    "paper": "PAPER_ID",
    "topic": "TOPIC_ID",
    "questionText": "Sample question with [IMAGE:1234567890.123:300x200px] image",
    "questionInlineImages": [{
      "id": 1234567890.123,
      "url": "data:image/png;base64,iVBORw0KG...",
      "width": 300,
      "height": 200,
      "type": "drawing"
    }],
    "answerText": "Answer with explanation",
    "answerInlineImages": [],
    "marks": 5
  }'
```

## 📊 Sample Data Structure

### Creating a Complete Subject
```javascript
{
  "name": "Physics",
  "description": "Physics subject",
  "papers": [
    {
      "name": "Paper 1",
      "description": "Mechanics and Electricity",
      "sections": ["Section A", "Section B"],
      "topics": ["Mechanics", "Electricity", "Magnetism"]
    },
    {
      "name": "Paper 2",
      "description": "Waves and Modern Physics",
      "sections": [],  // No sections
      "topics": ["Waves", "Optics", "Modern Physics"]
    }
  ]
}
```

## 🔒 Security Features

1. **Password Security**
   - bcrypt hashing with salt
   - Minimum 6 characters

2. **OTP Security**
   - 6-digit random code
   - 10-minute expiration
   - Max 5 verification attempts
   - Purpose-specific (registration/login/reset)

3. **JWT Security**
   - Token-based authentication
   - 7-day expiration (configurable)
   - User role included in token

4. **API Security**
   - Authentication required for all protected routes
   - Role-based authorization
   - Input validation on all endpoints

## 📝 Data Entry Workflow (Phase 1)

### Step 1: User Registration
1. User enters phone number and full name
2. System sends OTP to phone
3. User enters OTP to verify
4. User sets password
5. User receives JWT token

### Step 2: Add Subjects
1. Admin/Editor creates subject (e.g., "Mathematics")
2. Adds papers (e.g., "Paper 1", "Paper 2")
3. For each paper:
   - Optionally adds sections (e.g., "Section A", "Section B")
   - Adds topics (e.g., "Algebra", "Calculus")

### Step 3: Enter Questions
1. Editor selects subject → paper → topic (→ section if applicable)
2. Uses EditorDashboard to:
   - Type question text
   - Add images (upload/draw/graph)
   - Type answer with explanation
   - Set marks
3. Question saved with all metadata

### Step 4: Query and Filter
1. Filter questions by:
   - Subject
   - Paper
   - Topic
   - Section (if applicable)
   - Active/inactive status
2. Topics automatically filtered by selected paper
3. Search similar questions

## 🎯 Critical Concepts Implemented

✅ **1. Phone + OTP Authentication**
- User registers with phone number
- Receives OTP for verification
- Sets password after OTP confirmation
- Can reset password using OTP

✅ **2. Hierarchical Subject Structure**
- Subject → Papers → Topics → Questions
- Papers can have 0 or more sections
- Topics filtered by paper (not shared across papers)

✅ **3. Rich Content Support**
- Inline images in questions and answers
- Base64 encoding for storage
- Image metadata (dimensions, type)
- Placeholder format: `[IMAGE:id:300x200px]`

✅ **4. Flexible Section System**
- Papers can have no sections (empty array)
- Papers can have multiple sections
- Topics can optionally belong to sections

## 🌟 Integration with Frontend

The EditorDashboard (frontend) should connect to this API:

### Configuration
```javascript
// In frontend/exam/src/config.js
export const API_URL = 'http://localhost:5000/api';

// Store token after login
localStorage.setItem('token', response.token);

// Use token in requests
fetch(`${API_URL}/subjects`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

### Mapping Editor to API

**Subject Selection:**
```javascript
// Load subjects from API instead of hardcoded
const response = await fetch(`${API_URL}/subjects`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const subjects = await response.json();
```

**Paper Selection:**
```javascript
// Get papers for selected subject
const subject = subjects.find(s => s._id === selectedSubjectId);
const papers = subject.papers;
```

**Topic Filtering:**
```javascript
// Get topics for selected paper (filtered automatically)
const response = await fetch(
  `${API_URL}/subjects/${subjectId}/papers/${paperId}/topics`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const topics = await response.json();
```

**Save Question:**
```javascript
// Save question with inline images
await fetch(`${API_URL}/questions`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    subject: selectedSubjectId,
    paper: selectedPaperId,
    topic: selectedTopicId,
    section: selectedSectionId, // optional
    questionText: questionText, // contains [IMAGE:id:WxH] placeholders
    questionInlineImages: questionInlineImages, // array of image objects
    answerText: answerText,
    answerInlineImages: answerInlineImages,
    marks: marks
  })
});
```

## 📦 Dependencies Installed

```json
{
  "express": "^4.18.2",        // Web framework
  "mongoose": "^7.5.0",        // MongoDB ODM
  "bcryptjs": "^2.4.3",        // Password hashing
  "jsonwebtoken": "^9.0.2",    // JWT authentication
  "dotenv": "^16.3.1",         // Environment variables
  "cors": "^2.8.5"             // CORS middleware
}
```

## 🚧 Next Steps (Future Phases)

### Phase 2: Exam Paper Generation
- Select questions from bank
- Generate formatted PDF
- Include inline images
- Export to Word/PDF

### Phase 3: Exam Management
- Create exam sessions
- Schedule exams
- Assign students

### Phase 4: Answer Processing
- Upload answer sheets
- OCR recognition
- Automated marking (objective)
- Manual marking interface (subjective)

### Phase 5: Analytics & Reporting
- Question usage statistics
- Difficulty analysis
- Student performance tracking
- Comparative analysis

## 📚 Documentation Files

1. **README.md** - Complete setup and usage guide
2. **SCHEMA_DIAGRAM.md** - Visual database schema and API flows
3. **DEPLOYMENT.md** - This file - Complete package overview

## 🎓 Testing Credentials (After Seeding)

**Admin Account:**
- Phone: `+254700000000`
- Password: `admin123`
- Role: admin

**Editor Account:**
- Phone: `+254700000001`
- Password: `editor123`
- Role: editor

## ✅ Phase 1 Checklist

- ✅ MongoDB schema designed and implemented
- ✅ User authentication with phone + OTP
- ✅ Subject/Paper/Section/Topic hierarchy
- ✅ Topics filtered by paper
- ✅ Papers with 0 or more sections
- ✅ Question bank with rich content
- ✅ Inline image support (base64)
- ✅ RESTful API endpoints
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Database seeding script
- ✅ Complete documentation
- ✅ Ready for frontend integration

## 🎉 Summary

You now have a **complete, production-ready Phase 1 backend** for your Examination System with:

1. ✅ Phone authentication with OTP
2. ✅ Hierarchical subject organization
3. ✅ Flexible paper/section structure
4. ✅ Topic filtering by paper
5. ✅ Rich question bank with images
6. ✅ RESTful API
7. ✅ Security best practices
8. ✅ Database seeding
9. ✅ Complete documentation

**Ready to deploy and integrate with your React frontend!** 🚀
