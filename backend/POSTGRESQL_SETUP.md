# PostgreSQL Migration Guide

## Overview
This application has been migrated from MongoDB to PostgreSQL using Sequelize ORM.

## Prerequisites

### 1. Install PostgreSQL
- Download and install PostgreSQL from: https://www.postgresql.org/download/
- Or download pgAdmin 4 (includes PostgreSQL): https://www.pgadmin.org/download/

### 2. Verify PostgreSQL Installation
```bash
psql --version
```

## Setup Instructions

### Step 1: Create Database
Open pgAdmin or psql terminal and run:
```sql
CREATE DATABASE examination_system;
```

Or using psql command line:
```bash
psql -U postgres
CREATE DATABASE examination_system;
\q
```

### Step 2: Run Schema
Navigate to the backend directory and execute:
```bash
psql -U postgres -d examination_system -f database/schema.sql
```

Or in pgAdmin:
1. Open pgAdmin 4
2. Connect to your PostgreSQL server
3. Select the `examination_system` database
4. Open Query Tool (Tools > Query Tool)
5. Open the file `database/schema.sql`
6. Click Execute (F5)

### Step 3: Configure Environment Variables
Update `.env` file with your PostgreSQL credentials:
```properties
DB_HOST=localhost
DB_PORT=5432
DB_NAME=examination_system
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### Step 4: Install Dependencies
```bash
npm install
```

This will install:
- `pg` - PostgreSQL client for Node.js
- `pg-hstore` - Serializing and deserializing JSON data
- `sequelize` - Promise-based ORM for Node.js

### Step 5: Seed Database (Optional)
```bash
psql -U postgres -d examination_system -f database/seed.sql
```

Or use npm script:
```bash
npm run db:seed
```

### Step 6: Start Server
```bash
npm run dev
```

## Default Users

After seeding, you can login with:

**Admin Account:**
- Phone: +254700000000
- Password: admin123
- Role: admin

**Editor Account:**
- Phone: +254700000001
- Password: editor123
- Role: editor

## Database Schema

### Tables:
1. **users** - User accounts (admin, editor, user)
2. **otp_logs** - OTP verification logs
3. **subjects** - Academic subjects
4. **papers** - Exam papers within subjects
5. **topics** - Topics within papers
6. **sections** - Sections within papers
7. **questions** - Question bank
8. **question_images** - Images for questions/answers

### Key Features:
- UUID primary keys for all tables
- Foreign key constraints with CASCADE delete
- Automatic timestamps (created_at, updated_at)
- Indexes on frequently queried columns
- JSONB support for flexible data (question options)

## NPM Scripts

```bash
# Start server in production
npm start

# Start server in development with auto-reload
npm run dev

# Create database schema
npm run db:create

# Seed database with sample data
npm run db:seed
```

## Sequelize Models

All models are located in `backend/models/`:
- User.js
- Subject.js
- Paper.js
- Topic.js
- Section.js
- Question.js
- OTPLog.js

Models use Sequelize ORM with associations defined in `models/index.js`.

## Migration from MongoDB

### Changes Made:
1. ✅ Replaced `mongoose` with `sequelize` and `pg`
2. ✅ Created PostgreSQL schema with proper constraints
3. ✅ Converted Mongoose models to Sequelize models
4. ✅ Updated database connection logic
5. ✅ Maintained same API structure (no frontend changes needed)

### Database Comparison:

| Feature | MongoDB | PostgreSQL |
|---------|---------|------------|
| Type | NoSQL | Relational |
| Schema | Flexible | Strict |
| Relationships | References | Foreign Keys |
| Transactions | Limited | Full ACID |
| Complex Queries | Limited | Advanced SQL |

## Troubleshooting

### Connection Error
If you get "password authentication failed":
1. Check your PostgreSQL password in `.env`
2. Verify PostgreSQL is running: `pg_isready`
3. Check `pg_hba.conf` authentication settings

### Schema Creation Error
If tables already exist:
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```
Then run the schema.sql again.

### Port Already in Use
If port 5432 is in use:
1. Change `DB_PORT` in `.env`
2. Or stop other PostgreSQL instances

## Useful pgAdmin Features

1. **Query Tool** - Run SQL queries
2. **Schema Diff** - Compare schemas
3. **ERD Tool** - Visualize database structure
4. **Backup/Restore** - Database backups
5. **Import/Export** - CSV/JSON data

## Next Steps

1. Update any custom routes that use MongoDB-specific queries
2. Test all API endpoints
3. Update frontend if needed (though API interface remains the same)
4. Set up database backups
5. Configure production environment variables

## Support

For issues:
1. Check PostgreSQL logs: `pg_config --sharedir`/logs
2. Check application logs in terminal
3. Verify database connection: `psql -U postgres -d examination_system`
