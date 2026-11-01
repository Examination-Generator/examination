# Database Schema

Complete database structure for the Examination System.

## Overview

The database uses PostgreSQL with the following main entities:
- Users (authentication and roles)
- OTP Logs (verification codes)
- Subjects (top-level organization)
- Papers (exam papers)
- Topics (subject topics)
- Sections (exam sections)
- Questions (question bank)

## Entity Relationship

```
Users ──┐
        │
        ├──> Subjects ──> Papers ──┬──> Topics
        │                          │
        ├──> Topics                └──> Sections
        │
        ├──> Sections
        │
        └──> Questions
```

---

## 👤 Users Table

**Table Name:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| phone_number | VARCHAR(20) | UNIQUE, NOT NULL | Phone number (username) |
| full_name | VARCHAR(255) | NOT NULL | User's full name |
| password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| role | VARCHAR(20) | NOT NULL | user, editor, or admin |
| is_active | BOOLEAN | DEFAULT true | Account active status |
| is_staff | BOOLEAN | DEFAULT false | Django staff access |
| otp_verified | BOOLEAN | DEFAULT false | OTP verification status |
| last_login | TIMESTAMP | NULL | Last login timestamp |
| created_at | TIMESTAMP | AUTO | Account creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Indexes:**
- `phone_number` (unique)
- `created_at`

**Roles:**
- `user` - Basic read access
- `editor` - Can create/edit content
- `admin` - Full system access

---

## 📱 OTP Logs Table

**Table Name:** `otp_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique log identifier |
| phone_number | VARCHAR(20) | NOT NULL | Target phone number |
| otp | VARCHAR(6) | NOT NULL | OTP code |
| purpose | VARCHAR(20) | NOT NULL | registration, login, password_reset |
| status | VARCHAR(20) | DEFAULT 'sent' | sent, verified, expired, failed |
| expires_at | TIMESTAMP | NOT NULL | OTP expiration time |
| verified_at | TIMESTAMP | NULL | Verification timestamp |
| ip_address | INET | NULL | Request IP address |
| attempts | INTEGER | DEFAULT 0 | Verification attempts |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Indexes:**
- `phone_number, status`
- `expires_at`

---

## 📚 Subjects Table

**Table Name:** `subjects`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique subject identifier |
| name | VARCHAR(255) | UNIQUE, NOT NULL | Subject name |
| description | TEXT | NULL | Subject description |
| is_active | BOOLEAN | DEFAULT true | Active status |
| is_rollout_enabled | BOOLEAN | DEFAULT true | Visible to paper-generation users |
| created_by | UUID | FK → users | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Relationships:**
- `created_by` → `users.id` (SET NULL on delete)

---

## 📄 Papers Table

**Table Name:** `papers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique paper identifier |
| name | VARCHAR(255) | NOT NULL | Paper name |
| subject | UUID | FK → subjects | Parent subject |
| description | TEXT | NULL | Paper description |
| is_active | BOOLEAN | DEFAULT true | Active status |
| is_rollout_enabled | BOOLEAN | DEFAULT true | Visible to paper-generation users |
| created_by | UUID | FK → users | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Constraints:**
- UNIQUE(`subject`, `name`)

**Indexes:**
- `subject, is_active`

**Relationships:**
- `subject` → `subjects.id` (CASCADE on delete)
- `created_by` → `users.id` (SET NULL on delete)

---

## 📑 Topics Table

**Table Name:** `topics`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique topic identifier |
| name | VARCHAR(255) | NOT NULL | Topic name |
| paper | UUID | FK → papers | Parent paper |
| description | TEXT | NULL | Topic description |
| is_active | BOOLEAN | DEFAULT true | Active status |
| is_rollout_enabled | BOOLEAN | DEFAULT true | Visible to paper-generation users |
| created_by | UUID | FK → users | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Constraints:**
- UNIQUE(`paper`, `name`)

**Indexes:**
- `paper, is_active`

**Relationships:**
- `paper` → `papers.id` (CASCADE on delete)
- `created_by` → `users.id` (SET NULL on delete)

---

## 📋 Sections Table

**Table Name:** `sections`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique section identifier |
| name | VARCHAR(255) | NOT NULL | Section name |
| paper | UUID | FK → papers | Parent paper |
| description | TEXT | NULL | Section description |
| order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT true | Active status |
| created_by | UUID | FK → users | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Constraints:**
- UNIQUE(`paper`, `name`)

**Indexes:**
- `paper, is_active`

**Relationships:**
- `paper` → `papers.id` (CASCADE on delete)
- `created_by` → `users.id` (SET NULL on delete)

---

## ❓ Questions Table

**Table Name:** `questions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique question identifier |
| subject | UUID | FK → subjects | Subject reference |
| paper | UUID | FK → papers | Paper reference |
| topic | UUID | FK → topics | Topic reference |
| section | UUID | FK → sections | Section reference (optional) |
| question_text | TEXT | NOT NULL | Question content |
| answer_text | TEXT | NOT NULL | Answer content |
| question_inline_images | JSONB | DEFAULT [] | Base64 images array |
| answer_inline_images | JSONB | DEFAULT [] | Base64 images array |
| question_type | VARCHAR(20) | DEFAULT 'structured' | Question type |
| difficulty | VARCHAR(20) | DEFAULT 'medium' | easy, medium, hard |
| marks | INTEGER | NOT NULL | Mark allocation |
| options | JSONB | NULL | MCQ options (if applicable) |
| correct_answer | TEXT | NULL | Correct answer (if applicable) |
| answer_explanation | TEXT | NULL | Answer explanation |
| is_active | BOOLEAN | DEFAULT true | Active status |
| times_used | INTEGER | DEFAULT 0 | Usage counter |
| last_used | TIMESTAMP | NULL | Last usage timestamp |
| created_by | UUID | FK → users | Creator user ID |
| created_at | TIMESTAMP | AUTO | Creation time |
| updated_at | TIMESTAMP | AUTO | Last update time |

**Indexes:**
- `subject, paper, topic`
- `is_active`
- `question_type, difficulty`

**Relationships:**
- `subject` → `subjects.id` (CASCADE on delete)
- `paper` → `papers.id` (CASCADE on delete)
- `topic` → `topics.id` (CASCADE on delete)
- `section` → `sections.id` (SET NULL on delete)
- `created_by` → `users.id` (SET NULL on delete)

**Question Types:**
- `multiple_choice`
- `true_false`
- `short_answer`
- `essay`
- `structured`

---

## 🔗 Relationship Rules

### Validation Rules
1. **Paper** must belong to its **Subject**
2. **Topic** must belong to its **Paper**
3. **Section** must belong to its **Paper** (if set)
4. **Question** references must be consistent:
   - Topic's paper must match Question's paper
   - Paper's subject must match Question's subject
   - Section's paper must match Question's paper (if set)

### Cascade Behavior
- Delete Subject → Deletes all Papers, Topics, Questions
- Delete Paper → Deletes all Topics, Sections, Questions
- Delete Topic → Deletes all Questions referencing it
- Delete Section → Sets `section` to NULL in Questions
- Delete User → Sets `created_by` to NULL (preserves content)

---

## 📊 Example Data Structure

```
Subject: Mathematics
  ├── Paper: Paper 1 (Theory)
  │     ├── Section: Section A (Multiple Choice)
  │     ├── Section: Section B (Structured)
  │     ├── Topic: Algebra
  │     │     └── Questions: 50 questions
  │     └── Topic: Geometry
  │           └── Questions: 30 questions
  │
  └── Paper: Paper 2 (Practical)
        ├── Section: Section A (Experiments)
        ├── Topic: Calculus
        │     └── Questions: 25 questions
        └── Topic: Statistics
              └── Questions: 20 questions
```

---

## 🛠️ Database Migrations

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### View Migration Status
```bash
python manage.py showmigrations
```

---

## 🔍 Useful Queries

### Count Questions by Subject
```sql
SELECT 
    s.name as subject,
    COUNT(q.id) as question_count
FROM subjects s
LEFT JOIN questions q ON q.subject_id = s.id
GROUP BY s.id, s.name
ORDER BY question_count DESC;
```

### Find Questions Without Sections
```sql
SELECT id, question_text, marks
FROM questions
WHERE section_id IS NULL
LIMIT 10;
```

### User Activity Statistics
```sql
SELECT 
    u.full_name,
    u.role,
    COUNT(DISTINCT q.id) as questions_created,
    COUNT(DISTINCT s.id) as subjects_created
FROM users u
LEFT JOIN questions q ON q.created_by_id = u.id
LEFT JOIN subjects s ON s.created_by_id = u.id
GROUP BY u.id, u.full_name, u.role
ORDER BY questions_created DESC;
```

### Questions by Difficulty
```sql
SELECT 
    difficulty,
    COUNT(*) as count,
    SUM(marks) as total_marks
FROM questions
WHERE is_active = true
GROUP BY difficulty;
```
