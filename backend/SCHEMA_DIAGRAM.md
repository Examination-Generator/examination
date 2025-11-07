# Examination System - Database Schema & API Flow

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXAMINATION SYSTEM                          │
│                         MongoDB Collections                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│       USERS          │
├──────────────────────┤
│ _id                  │
│ fullName             │
│ phoneNumber (unique) │◄──────┐
│ password (hashed)    │       │
│ otp: {               │       │
│   code               │       │
│   expiresAt          │       │ (createdBy)
│   verified           │       │
│ }                    │       │
│ isActive             │       │
│ role                 │       │
│ lastLogin            │       │
└──────────────────────┘       │
                               │
┌──────────────────────┐       │
│      SUBJECTS        │       │
├──────────────────────┤       │
│ _id                  │       │
│ name (unique)        │       │
│ description          │       │
│ papers: [ObjectId]───┼───┐   │
│ isActive             │   │   │
│ createdBy ───────────┼───┼───┘
└──────────────────────┘   │
                           │
┌──────────────────────┐   │
│       PAPERS         │◄──┘
├──────────────────────┤
│ _id                  │
│ name                 │
│ subject: ObjectId────┼───┐
│ sections: [ObjectId]─┼───┼───┐
│ topics: [ObjectId]───┼───┼───┼───┐
│ description          │   │   │   │
│ isActive             │   │   │   │
│ createdBy ───────────┼───┼───┼───┼───┐
└──────────────────────┘   │   │   │   │
                           │   │   │   │
┌──────────────────────┐   │   │   │   │
│      SECTIONS        │◄──┼───┘   │   │
├──────────────────────┤   │       │   │
│ _id                  │   │       │   │
│ name                 │   │       │   │
│ paper: ObjectId──────┼───┘       │   │
│ order                │           │   │
│ description          │           │   │
│ isActive             │           │   │
│ createdBy ───────────┼───────────┼───┤
└──────────────────────┘           │   │
                                   │   │
┌──────────────────────┐           │   │
│       TOPICS         │◄──────────┘   │
├──────────────────────┤               │
│ _id                  │               │
│ name                 │               │
│ paper: ObjectId──────┼───┐           │
│ section: ObjectId────┼───┼───┐       │
│ description          │   │   │       │
│ isActive             │   │   │       │
│ createdBy ───────────┼───┼───┼───────┤
└──────────────────────┘   │   │       │
                           │   │       │
┌──────────────────────┐   │   │       │
│      QUESTIONS       │   │   │       │
├──────────────────────┤   │   │       │
│ _id                  │   │   │       │
│ subject: ObjectId────┼───┤   │       │
│ paper: ObjectId──────┼───┘   │       │
│ topic: ObjectId──────┼───────┘       │
│ section: ObjectId────┼───────────┐   │
│ questionText         │           │   │
│ questionInlineImages │           │   │
│   [{                 │           │   │
│     id: Number       │           │   │
│     url: String      │           │   │
│     width: Number    │           │   │
│     height: Number   │           │   │
│     type: String     │           │   │
│   }]                 │           │   │
│ answerText           │           │   │
│ answerInlineImages   │           │   │
│ marks                │           │   │
│ isActive             │           │   │
│ timesUsed            │           │   │
│ lastUsed             │           │   │
│ createdBy ───────────┼───────────┼───┘
└──────────────────────┘           │
                                   │
┌──────────────────────┐           │
│      OTP LOGS        │           │
├──────────────────────┤           │
│ _id                  │           │
│ phoneNumber          │           │
│ otp                  │           │
│ purpose              │           │
│ status               │           │
│ expiresAt (TTL)      │           │
│ verifiedAt           │           │
│ attempts             │           │
└──────────────────────┘           │
                                   │
┌──────────────────────┐           │
│      SESSIONS        │           │
├──────────────────────┤           │
│ _id                  │           │
│ user: ObjectId───────┼───────────┘
│ token (unique)       │
│ ipAddress            │
│ userAgent            │
│ expiresAt (TTL)      │
└──────────────────────┘
```

## Hierarchical Relationship

```
User
│
└── Subject
    └── Paper
        ├── Section (0 or more)
        └── Topic (filtered by paper)
            └── Question
```

## API Flow Diagram

### 1. User Registration Flow

```
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Client  │          │   API   │          │Database │
└────┬────┘          └────┬────┘          └────┬────┘
     │                    │                     │
     │  POST /send-otp    │                     │
     ├───────────────────►│                     │
     │  {phoneNumber}     │                     │
     │                    │  Check if exists    │
     │                    ├────────────────────►│
     │                    │                     │
     │                    │  Generate OTP       │
     │                    │  Save to OTPLog     │
     │                    ├────────────────────►│
     │                    │                     │
     │                    │  Send SMS (mock)    │
     │   OTP sent ✓       │                     │
     │◄───────────────────┤                     │
     │                    │                     │
     │  POST /verify-otp  │                     │
     ├───────────────────►│                     │
     │  {phone, otp}      │                     │
     │                    │  Verify OTP         │
     │                    ├────────────────────►│
     │                    │                     │
     │   Verified ✓       │  Update status      │
     │◄───────────────────┤◄────────────────────┤
     │                    │                     │
     │  POST /register    │                     │
     ├───────────────────►│                     │
     │  {phone, name,     │                     │
     │   password}        │  Hash password      │
     │                    │  Create user        │
     │                    ├────────────────────►│
     │                    │                     │
     │   JWT Token        │  Generate token     │
     │◄───────────────────┤◄────────────────────┤
     │                    │                     │
```

### 2. Subject Creation Flow

```
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Client  │          │   API   │          │Database │
└────┬────┘          └────┬────┘          └────┬────┘
     │                    │                     │
     │  POST /subjects    │                     │
     ├───────────────────►│                     │
     │  Authorization:    │                     │
     │  Bearer <token>    │  Verify JWT         │
     │                    │                     │
     │  {                 │  Create Subject     │
     │    name,           ├────────────────────►│
     │    papers: [       │                     │
     │      {name,        │  Create Papers      │
     │       sections,    ├────────────────────►│
     │       topics}      │                     │
     │    ]               │  Create Sections    │
     │  }                 ├────────────────────►│
     │                    │                     │
     │                    │  Create Topics      │
     │                    ├────────────────────►│
     │                    │                     │
     │                    │  Link relationships │
     │                    ├────────────────────►│
     │                    │                     │
     │   Subject created  │  Return populated   │
     │   with all         │  subject            │
     │   relations ✓      │◄────────────────────┤
     │◄───────────────────┤                     │
     │                    │                     │
```

### 3. Question Creation Flow

```
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Editor  │          │   API   │          │Database │
│Dashboard│          │         │          │         │
└────┬────┘          └────┬────┘          └────┬────┘
     │                    │                     │
     │  User types        │                     │
     │  question text     │                     │
     │                    │                     │
     │  User adds image   │                     │
     │  (upload/draw/     │                     │
     │   graph paper)     │                     │
     │                    │                     │
     │  [IMAGE:id:WxH]    │                     │
     │  placeholder       │                     │
     │  inserted          │                     │
     │                    │                     │
     │  POST /questions   │                     │
     ├───────────────────►│                     │
     │  {                 │  Verify JWT         │
     │   subject,         │                     │
     │   paper,           │  Validate refs      │
     │   topic,           ├────────────────────►│
     │   section,         │                     │
     │   questionText,    │  Create question    │
     │   questionInline   │  with images        │
     │     Images: [{     ├────────────────────►│
     │       id,          │                     │
     │       url: base64, │                     │
     │       width,       │  Store base64       │
     │       height,      │  images             │
     │       type         │                     │
     │     }],            │                     │
     │   answerText,      │                     │
     │   answerInline     │                     │
     │     Images,        │                     │
     │   marks            │                     │
     │  }                 │                     │
     │                    │                     │
     │   Question saved ✓ │  Return question    │
     │◄───────────────────┤◄────────────────────┤
     │                    │                     │
```

### 4. Filtering Topics by Paper

```
┌─────────┐          ┌─────────┐          ┌─────────┐
│ Client  │          │   API   │          │Database │
└────┬────┘          └────┬────┘          └────┬────┘
     │                    │                     │
     │  GET /subjects     │                     │
     ├───────────────────►│                     │
     │                    │  Get all subjects   │
     │                    │  with papers        │
     │                    ├────────────────────►│
     │                    │                     │
     │   [subjects]       │  Populate papers    │
     │◄───────────────────┤◄────────────────────┤
     │                    │                     │
     │  User selects      │                     │
     │  Subject: Math     │                     │
     │                    │                     │
     │  User selects      │                     │
     │  Paper: Paper 1    │                     │
     │                    │                     │
     │  GET /subjects/    │                     │
     │  {subId}/papers/   │                     │
     │  {paperId}/topics  │                     │
     ├───────────────────►│                     │
     │                    │  Filter topics      │
     │                    │  WHERE paper=id     │
     │                    ├────────────────────►│
     │                    │                     │
     │   [topics for      │  Return filtered    │
     │    Paper 1 only]   │  topics             │
     │◄───────────────────┤◄────────────────────┤
     │                    │                     │
```

## Authentication & Authorization

```
┌─────────────────────────────────────────────────────────┐
│                  JWT Authentication                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. User logs in with phone + password                 │
│  2. Server generates JWT token                         │
│  3. Client stores token (localStorage/sessionStorage)  │
│  4. Client sends token in Authorization header:        │
│     Authorization: Bearer <token>                      │
│  5. Server validates token on each request             │
│  6. Token contains: userId, role, expiration           │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Role-Based Access                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Admin:  Full access to all operations                 │
│          - User management                              │
│          - Subject/Paper/Topic CRUD                     │
│          - Question CRUD                                │
│                                                         │
│  Editor: Data entry permissions                         │
│          - Create/Edit questions                        │
│          - View subjects/papers/topics                  │
│          - Cannot delete or manage users                │
│                                                         │
│  Viewer: Read-only access                               │
│          - View questions                               │
│          - View subjects/papers/topics                  │
│          - Cannot create or modify                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Image Handling Flow

```
┌──────────────────────────────────────────────────────────┐
│              Image Types Supported                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Upload: User uploads image file                     │
│     - Converted to base64                                │
│     - Stored in questionInlineImages                     │
│                                                          │
│  2. Drawing: User draws on canvas                       │
│     - Canvas exported to PNG (2x resolution)             │
│     - Converted to base64                                │
│     - Auto-inserted with placeholder                     │
│                                                          │
│  3. Graph Paper: Pre-formatted grid canvas              │
│     - 10px unit squares                                  │
│     - Exported same as drawing                           │
│                                                          │
│  Storage Format:                                         │
│  {                                                       │
│    id: 1234567890.123,        // Float ID                │
│    url: "data:image/png;base64,...",                    │
│    width: 300,                 // Display width          │
│    height: 200,                // Display height         │
│    type: "drawing"             // upload|drawing|graph   │
│  }                                                       │
│                                                          │
│  Placeholder in text:                                    │
│  [IMAGE:1234567890.123:300x200px]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Next Steps for Phase 2

1. **Question Paper Generation**
   - Select questions from bank
   - Generate formatted PDF
   - Include images and formatting

2. **Exam Management**
   - Create exam sessions
   - Assign papers to exams
   - Track exam schedules

3. **Answer Sheet Processing**
   - Upload answer sheets
   - OCR processing
   - Mark allocation

4. **Reporting & Analytics**
   - Question usage statistics
   - Difficulty analysis
   - Performance tracking
