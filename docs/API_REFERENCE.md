# API Reference

Complete reference for all API endpoints in the Examination System.

## Base URL

**Production:** `https://examination-s3np.vercel.app/api`  
**Local Development:** `http://localhost:8000/api`

## Authentication

Most endpoints require authentication via JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All responses follow this structure:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ...result data... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": { ...error details... }
}
```

---

## 🔐 Authentication Endpoints

### Login
```http
POST /api/login
```

**Request:**
```json
{
  "phoneNumber": "0000000001",
  "password": "0000"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "fullName": "System Admin",
      "phoneNumber": "0000000001",
      "role": "admin"
    }
  }
}
```

### Send OTP (Future)
```http
POST /api/send-otp
```

**Request:**
```json
{
  "phoneNumber": "1234567890",
  "purpose": "registration"
}
```

### Verify OTP (Future)
```http
POST /api/verify-otp
```

**Request:**
```json
{
  "phoneNumber": "1234567890",
  "otp": "123456",
  "purpose": "registration"
}
```

### Register (Future)
```http
POST /api/register
```

**Request:**
```json
{
  "phoneNumber": "1234567890",
  "fullName": "John Doe",
  "password": "1234",
  "role": "editor"
}
```

---

## 🗄️ Database Management

### Database Health Check
```http
GET /api/database/health
```

**Response:**
```json
{
  "success": true,
  "message": "Database status: healthy",
  "data": {
    "database_connected": true,
    "tables_exist": true,
    "can_query": true,
    "migrations_needed": false,
    "user_count": 2
  }
}
```

### Initialize Database
```http
POST /api/database/initialize
```

Runs migrations and sets up database tables.

### Create Default Users
```http
POST /api/database/create-defaults
```

Creates admin and editor default users if they don't exist.

---

## 📚 Subject Endpoints

### List All Subjects
```http
GET /api/subjects
```

**Query Parameters:**
- `is_active` (optional): Filter by active status (true/false)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Mathematics",
      "description": "Math subject",
      "is_active": true,
      "papers": [...],
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Create Subject
```http
POST /api/subjects
```

**Request:**
```json
{
  "name": "Physics",
  "description": "Science subject",
  "papers": [
    {
      "name": "Paper 1",
      "description": "Theory",
      "sections": ["Section A", "Section B"],
      "topics": ["Mechanics", "Thermodynamics"]
    }
  ]
}
```

**Authentication:** Required (Editor or Admin)

### Get Subject Details
```http
GET /api/subjects/{subject_id}
```

### Update Subject
```http
PUT /api/subjects/{subject_id}
```

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "is_active": true
}
```

**Authentication:** Required (Editor or Admin)

### Delete Subject
```http
DELETE /api/subjects/{subject_id}
```

**Authentication:** Required (Admin only)

---

## 📄 Paper Endpoints

### Add Paper to Subject
```http
POST /api/subjects/{subject_id}/papers
```

**Request:**
```json
{
  "name": "Paper 2",
  "description": "Practical paper"
}
```

**Authentication:** Required (Editor or Admin)

### Get Paper Details
```http
GET /api/subjects/{subject_id}/papers/{paper_id}
```

**Response includes:** Paper details, sections, and topics

---

## 📑 Topic Endpoints

### Add Topic to Paper
```http
POST /api/subjects/{subject_id}/papers/{paper_id}/topics
```

**Request:**
```json
{
  "name": "Algebra",
  "description": "Algebraic concepts"
}
```

**Authentication:** Required (Editor or Admin)

### Get All Topics for Paper
```http
GET /api/subjects/{subject_id}/papers/{paper_id}/topics
```

### Get Topic Details
```http
GET /api/subjects/topics/{topic_id}
```

### Update Topic
```http
PUT /api/subjects/topics/{topic_id}
```

### Delete Topic
```http
DELETE /api/subjects/topics/{topic_id}
```

---

## 📋 Section Endpoints

### Add Section to Paper
```http
POST /api/subjects/{subject_id}/papers/{paper_id}/sections
```

**Request:**
```json
{
  "name": "Section A",
  "description": "Multiple choice",
  "order": 1
}
```

**Authentication:** Required (Editor or Admin)

### Get Section Details
```http
GET /api/subjects/sections/{section_id}
```

### Update Section
```http
PUT /api/subjects/sections/{section_id}
```

### Delete Section
```http
DELETE /api/subjects/sections/{section_id}
```

---

## ❓ Question Endpoints

### List Questions
```http
GET /api/questions
```

**Query Parameters:**
- `subject` (uuid): Filter by subject
- `paper` (uuid): Filter by paper
- `topic` (uuid): Filter by topic
- `section` (uuid): Filter by section
- `difficulty` (easy/medium/hard): Filter by difficulty
- `question_type`: Filter by type
- `is_active` (true/false): Filter by status

### Create Question
```http
POST /api/questions
```

**Request:**
```json
{
  "subject": "uuid",
  "paper": "uuid",
  "topic": "uuid",
  "section": "uuid",
  "question_text": "What is 2 + 2?",
  "answer_text": "4",
  "question_inline_images": ["base64-encoded-image"],
  "answer_inline_images": ["base64-encoded-image"],
  "question_type": "multiple_choice",
  "difficulty": "easy",
  "marks": 2,
  "options": ["2", "3", "4", "5"],
  "correct_answer": "4",
  "is_active": true
}
```

**Authentication:** Required (Editor or Admin)

### Get Question Details
```http
GET /api/questions/{question_id}
```

### Update Question
```http
PUT /api/questions/{question_id}
```

### Delete Question
```http
DELETE /api/questions/{question_id}
```

### Bulk Create Questions
```http
POST /api/questions/bulk
```

**Request:**
```json
{
  "questions": [
    { ...question1... },
    { ...question2... },
    { ...question3... }
  ]
}
```

### Search Similar Questions
```http
POST /api/questions/search-similar
```

**Request:**
```json
{
  "question_text": "What is photosynthesis?",
  "subject": "uuid",
  "paper": "uuid"
}
```

### Question Statistics
```http
GET /api/questions/stats/overview
```

**Query Parameters:**
- `subject` (uuid): Filter stats by subject
- `paper` (uuid): Filter stats by paper

**Response:**
```json
{
  "success": true,
  "data": {
    "total_questions": 150,
    "by_difficulty": {
      "easy": 50,
      "medium": 75,
      "hard": 25
    },
    "by_type": {
      "multiple_choice": 80,
      "structured": 70
    },
    "active_questions": 145,
    "inactive_questions": 5
  }
}
```

---

## 📊 Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## 🔑 Authentication Token Usage

After login, include the token in all subsequent requests:

**PowerShell:**
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "$baseUrl/api/subjects" -Headers $headers
```

**Curl:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     https://examination-s3np.vercel.app/api/subjects
```

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- UUIDs are used for all resource IDs
- Images are stored as base64-encoded strings in `question_inline_images` and `answer_inline_images` arrays
- Default users bypass OTP verification until SMS service is configured
