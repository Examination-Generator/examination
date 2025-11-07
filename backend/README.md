# Examination System - Backend API

## Overview

This is the backend API for the Examination System, built with Node.js, Express, and MongoDB. It provides RESTful endpoints for user authentication, subject management, and question bank functionality.

## Features

### Phase 1: Data Entry System

- ✅ **User Authentication**
  - Phone number registration with OTP verification
  - Password-based login
  - JWT token-based authentication
  - Password reset functionality

- ✅ **Subject Management**
  - Hierarchical structure: Subject → Papers → Topics
  - Papers can have 0 or more Sections
  - Topics are filtered by Paper
  - Full CRUD operations

- ✅ **Question Bank**
  - Rich content support with inline images
  - Support for drawings and graph paper images
  - Image metadata (dimensions, type)
  - Question classification by subject, paper, topic, and section
  - Marks allocation
  - Question status management
  - Search and filter capabilities

## Database Schema

### Collections

1. **users** - User accounts with phone authentication
2. **subjects** - Root level subjects
3. **papers** - Papers belonging to subjects
4. **sections** - Optional sections within papers
5. **topics** - Topics belonging to papers
6. **questions** - Questions with rich content support
7. **otplogs** - OTP verification tracking
8. **sessions** - User session management

### Schema Hierarchy

```
User (Phone + OTP Auth)
│
├── Subject
│   └── Paper
│       ├── Section (0 or more)
│       └── Topic (filtered by paper)
│           └── Question
```

## Installation

### Prerequisites

- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn

### Setup Steps

1. **Install dependencies:**
   ```bash
   cd backend
   npm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   MONGODB_URI=mongodb://localhost:27017/examination_system
   JWT_SECRET=your-super-secret-jwt-key
   JWT_EXPIRES_IN=7d
   PORT=5000
   ```

3. **Start MongoDB:**
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

4. **Seed the database (optional):**
   ```bash
   npm run seed
   ```
   
   This creates:
   - Admin user: `+254700000000` / `admin123`
   - Editor user: `+254700000001` / `editor123`
   - Sample subjects, papers, and questions

5. **Start the server:**
   ```bash
   # Development mode (with auto-restart)
   npm run dev
   
   # Production mode
   npm start
   ```

6. **Verify installation:**
   ```bash
   # Health check
   curl http://localhost:5000/api/health
   ```

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### 1. Send OTP
```http
POST /api/auth/send-otp
Content-Type: application/json

{
  "phoneNumber": "+254700000000",
  "purpose": "registration" // or "login", "password_reset"
}
```

#### 2. Verify OTP
```http
POST /api/auth/verify-otp
Content-Type: application/json

{
  "phoneNumber": "+254700000000",
  "otp": "123456"
}
```

#### 3. Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "phoneNumber": "+254700000000",
  "fullName": "John Doe",
  "password": "secure123"
}
```

#### 4. Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "phoneNumber": "+254700000000",
  "password": "secure123"
}
```

### Subject Management Endpoints

#### 1. Create Subject with Papers
```http
POST /api/subjects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Mathematics",
  "description": "Math subject",
  "papers": [
    {
      "name": "Paper 1",
      "description": "Algebra and Calculus",
      "sections": ["Section A", "Section B"],
      "topics": ["Algebra", "Calculus"]
    },
    {
      "name": "Paper 2",
      "sections": [],
      "topics": ["Geometry", "Trigonometry"]
    }
  ]
}
```

#### 2. Get All Subjects
```http
GET /api/subjects
Authorization: Bearer <token>
```

#### 3. Get Topics by Paper
```http
GET /api/subjects/:subjectId/papers/:paperId/topics
Authorization: Bearer <token>
```

### Question Management Endpoints

#### 1. Create Question
```http
POST /api/questions
Authorization: Bearer <token>
Content-Type: application/json

{
  "subject": "subject_id",
  "paper": "paper_id",
  "topic": "topic_id",
  "section": "section_id", // optional
  "questionText": "Question with [IMAGE:1234567890.123:300x200px] placeholder",
  "questionInlineImages": [
    {
      "id": 1234567890.123,
      "url": "data:image/png;base64,...",
      "width": 300,
      "height": 200,
      "type": "drawing"
    }
  ],
  "answerText": "Answer with explanation",
  "answerInlineImages": [],
  "marks": 5
}
```

#### 2. Get Questions with Filters
```http
GET /api/questions?subject=xxx&paper=xxx&topic=xxx&page=1&limit=50
Authorization: Bearer <token>
```

#### 3. Search Similar Questions
```http
GET /api/questions/search/similar?text=calculate%20area&limit=10
Authorization: Bearer <token>
```

#### 4. Bulk Create Questions
```http
POST /api/questions/bulk
Authorization: Bearer <token>
Content-Type: application/json

{
  "questions": [
    { /* question 1 */ },
    { /* question 2 */ },
    { /* question 3 */ }
  ]
}
```

## Data Models

### User Model
```javascript
{
  fullName: String,
  phoneNumber: String (unique),
  password: String (hashed),
  otp: {
    code: String,
    expiresAt: Date,
    verified: Boolean
  },
  isActive: Boolean,
  role: 'admin' | 'editor' | 'viewer',
  lastLogin: Date
}
```

### Subject Model
```javascript
{
  name: String (unique),
  description: String,
  papers: [ObjectId],
  isActive: Boolean,
  createdBy: ObjectId
}
```

### Paper Model
```javascript
{
  name: String,
  subject: ObjectId,
  sections: [ObjectId],
  topics: [ObjectId],
  isActive: Boolean,
  createdBy: ObjectId
}
```

### Topic Model
```javascript
{
  name: String,
  paper: ObjectId,
  section: ObjectId (optional),
  isActive: Boolean,
  createdBy: ObjectId
}
```

### Question Model
```javascript
{
  subject: ObjectId,
  paper: ObjectId,
  topic: ObjectId,
  section: ObjectId (optional),
  questionText: String,
  questionInlineImages: [{
    id: Number,
    url: String,
    width: Number,
    height: Number,
    type: 'upload' | 'drawing' | 'graph'
  }],
  answerText: String,
  answerInlineImages: [...],
  marks: Number,
  isActive: Boolean,
  timesUsed: Number,
  createdBy: ObjectId
}
```

## Security

- **Password Hashing**: bcryptjs with salt rounds
- **JWT Authentication**: Token-based with expiration
- **OTP Verification**: 10-minute expiration, max 5 attempts
- **Input Validation**: All inputs validated and sanitized
- **Role-Based Access**: Admin, Editor, Viewer roles

## Error Handling

All API responses follow this format:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { /* response data */ }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description"
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

## Development

### Project Structure
```
backend/
├── config/
│   └── database.js          # MongoDB connection
├── middleware/
│   └── auth.js              # Authentication middleware
├── models/
│   └── schema.js            # Mongoose schemas
├── routes/
│   ├── auth.js              # Authentication routes
│   ├── subjects.js          # Subject management routes
│   └── questions.js         # Question management routes
├── scripts/
│   └── seedDatabase.js      # Database seeding script
├── .env.example             # Environment variables template
├── package.json             # Dependencies
└── server.js                # Main server file
```

### Available Scripts

```bash
npm start       # Start production server
npm run dev     # Start development server with nodemon
npm run seed    # Seed database with sample data
```

## SMS Integration

The OTP system is designed to work with SMS providers. To integrate:

1. Choose an SMS provider (Twilio, Africa's Talking, etc.)
2. Add credentials to `.env`
3. Update the `sendSMS` function in `routes/auth.js`

Example for Africa's Talking:
```javascript
const AfricasTalking = require('africastalking');
const africastalking = AfricasTalking({
    apiKey: process.env.SMS_API_KEY,
    username: process.env.SMS_USERNAME
});

const sendSMS = async (phoneNumber, message) => {
    try {
        const result = await africastalking.SMS.send({
            to: [phoneNumber],
            message: message,
            from: process.env.SMS_SENDER_ID
        });
        return { success: true, result };
    } catch (error) {
        console.error('SMS error:', error);
        return { success: false, error };
    }
};
```

## Deployment

### Production Checklist

- [ ] Set strong JWT_SECRET
- [ ] Use MongoDB Atlas or managed MongoDB
- [ ] Enable MongoDB authentication
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for production domain
- [ ] Set NODE_ENV=production
- [ ] Enable rate limiting
- [ ] Set up logging (Winston, Morgan)
- [ ] Configure backup strategy
- [ ] Set up monitoring (PM2, New Relic)

### Environment Variables for Production

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
JWT_SECRET=very-long-random-secret-key
NODE_ENV=production
PORT=5000
ALLOWED_ORIGINS=https://yourdomain.com
SMS_PROVIDER=africastalking
SMS_API_KEY=your_api_key
```

## Testing

Test the API using:
- Postman/Insomnia
- curl commands
- Frontend integration

### Example Test Flow

1. **Register User:**
   ```bash
   # Send OTP
   curl -X POST http://localhost:5000/api/auth/send-otp \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "+254700000000", "purpose": "registration"}'
   
   # Verify OTP (use code from console)
   curl -X POST http://localhost:5000/api/auth/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "+254700000000", "otp": "123456"}'
   
   # Complete registration
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "+254700000000", "fullName": "Test User", "password": "test123"}'
   ```

2. **Login and Get Token:**
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "+254700000000", "password": "test123"}'
   ```

3. **Use Token for Authenticated Requests:**
   ```bash
   curl http://localhost:5000/api/subjects \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Support

For issues or questions:
- Create an issue in the repository
- Contact the development team

## License

ISC License
