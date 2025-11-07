# Database Migration Scripts

## Export Database from Vercel Postgres

### Windows PowerShell
```powershell
# Set variables
$VERCEL_DB_URL = "postgres://default:PASSWORD@HOST/verceldb?sslmode=require"
$BACKUP_FILE = "backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').sql"

# Export database
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" "$VERCEL_DB_URL" > $BACKUP_FILE

Write-Host "Database exported to $BACKUP_FILE"
```

### Linux/Mac
```bash
#!/bin/bash
# Export database from Vercel Postgres

VERCEL_DB_URL="postgres://default:PASSWORD@HOST/verceldb?sslmode=require"
BACKUP_FILE="backup_$(date +%Y-%m-%d_%H-%M-%S).sql"

pg_dump "$VERCEL_DB_URL" > "$BACKUP_FILE"

echo "Database exported to $BACKUP_FILE"
```

## Import Database to Cloud Provider

### AWS RDS
```bash
#!/bin/bash
# Import to AWS RDS

BACKUP_FILE="backup.sql"
AWS_DB_URL="postgres://admin:password@your-rds-instance.region.rds.amazonaws.com:5432/examdb"

psql "$AWS_DB_URL" < "$BACKUP_FILE"

echo "Database imported to AWS RDS"
```

### Azure Database for PostgreSQL
```bash
#!/bin/bash
# Import to Azure Database

BACKUP_FILE="backup.sql"
AZURE_DB_URL="postgres://adminuser@servername:password@servername.postgres.database.azure.com:5432/examdb?sslmode=require"

psql "$AZURE_DB_URL" < "$BACKUP_FILE"

echo "Database imported to Azure Database"
```

### Google Cloud SQL
```bash
#!/bin/bash
# Import to Google Cloud SQL

BACKUP_FILE="backup.sql"
GCP_DB_URL="postgres://postgres:password@/examdb?host=/cloudsql/project:region:instance"

psql "$GCP_DB_URL" < "$BACKUP_FILE"

echo "Database imported to Google Cloud SQL"
```

## Python Script for Database Migration

```python
#!/usr/bin/env python
"""
Database migration script for moving from Vercel Postgres to cloud database
"""
import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.production')

# Database URLs
VERCEL_DB_URL = os.getenv('POSTGRES_URL')
CLOUD_DB_URL = os.getenv('CLOUD_DATABASE_URL')  # Your cloud database URL

def export_database():
    """Export database from Vercel Postgres"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = f'backup_{timestamp}.sql'
    
    print(f"Exporting database from Vercel...")
    cmd = f'pg_dump "{VERCEL_DB_URL}" > {backup_file}'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Database exported to {backup_file}")
        return backup_file
    else:
        print(f"✗ Export failed: {result.stderr}")
        return None

def import_database(backup_file):
    """Import database to cloud provider"""
    if not CLOUD_DB_URL:
        print("✗ CLOUD_DATABASE_URL not set in environment variables")
        return False
    
    print(f"Importing database to cloud provider...")
    cmd = f'psql "{CLOUD_DB_URL}" < {backup_file}'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Database imported successfully")
        return True
    else:
        print(f"✗ Import failed: {result.stderr}")
        return False

def migrate_database():
    """Complete migration process"""
    print("=" * 60)
    print("Database Migration Tool")
    print("=" * 60)
    
    # Step 1: Export from Vercel
    backup_file = export_database()
    if not backup_file:
        return
    
    # Step 2: Import to cloud
    success = import_database(backup_file)
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print(f"\nBackup file: {backup_file}")
        print("\nNext steps:")
        print("1. Update POSTGRES_URL in Vercel environment variables")
        print("2. Update CORS_ALLOWED_ORIGINS if database host changed")
        print("3. Redeploy backend on Vercel")
        print("4. Test the application")
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)

if __name__ == '__main__':
    migrate_database()
```

## Manual Migration Steps

### 1. Prepare Cloud Database

```sql
-- Connect to your cloud database
psql "your-cloud-database-url"

-- Create database (if not exists)
CREATE DATABASE examdb;

-- Create user (if needed)
CREATE USER examuser WITH PASSWORD 'your-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE examdb TO examuser;
```

### 2. Export from Vercel Postgres

```bash
# Get the connection string from Vercel dashboard
# Storage > Postgres > .env.local > POSTGRES_URL

# Export
pg_dump "postgres://default:PASSWORD@HOST/verceldb?sslmode=require" > backup.sql
```

### 3. Import to Cloud Database

```bash
# Import to your cloud database
psql "your-cloud-database-url" < backup.sql
```

### 4. Update Environment Variables on Vercel

Update these variables in your Vercel backend project:

```
POSTGRES_URL=your-cloud-database-url
POSTGRES_HOST=your-cloud-host
POSTGRES_DATABASE=examdb
POSTGRES_USER=examuser
POSTGRES_PASSWORD=your-password
```

### 5. Redeploy Backend

```bash
cd django_backend
vercel --prod
```

### 6. Test Connection

```bash
# Test with Django management command
python manage.py dbshell --settings=examination_system.settings_production
```

## Scheduled Backups

### Using cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-File C:\path\to\backup_script.ps1`

### Vercel Function for Automatic Backups (Advanced)

```javascript
// api/backup.js
import { sql } from '@vercel/postgres';
import { execSync } from 'child_process';

export default async function handler(req, res) {
  // Verify authorization
  if (req.headers.authorization !== `Bearer ${process.env.BACKUP_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupFile = `backup_${timestamp}.sql`;
    
    // Run pg_dump
    execSync(`pg_dump "${process.env.POSTGRES_URL}" > /tmp/${backupFile}`);
    
    // Upload to S3 or other storage
    // ... (implementation depends on storage provider)
    
    res.status(200).json({ 
      success: true, 
      message: 'Backup completed',
      file: backupFile 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
}
```

## Data Validation After Migration

```python
#!/usr/bin/env python
"""
Validate data after migration
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.production')

def validate_migration():
    """Compare record counts between old and new databases"""
    
    # Connect to both databases
    vercel_conn = psycopg2.connect(os.getenv('POSTGRES_URL'))
    cloud_conn = psycopg2.connect(os.getenv('CLOUD_DATABASE_URL'))
    
    vercel_cur = vercel_conn.cursor()
    cloud_cur = cloud_conn.cursor()
    
    # Tables to check
    tables = ['api_user', 'api_subject', 'api_paper', 'api_topic', 
              'api_section', 'api_question', 'api_otp']
    
    print("Validating migration...")
    print("-" * 60)
    
    all_match = True
    
    for table in tables:
        vercel_cur.execute(f"SELECT COUNT(*) FROM {table}")
        vercel_count = vercel_cur.fetchone()[0]
        
        cloud_cur.execute(f"SELECT COUNT(*) FROM {table}")
        cloud_count = cloud_cur.fetchone()[0]
        
        status = "✓" if vercel_count == cloud_count else "✗"
        print(f"{status} {table}: Vercel={vercel_count}, Cloud={cloud_count}")
        
        if vercel_count != cloud_count:
            all_match = False
    
    print("-" * 60)
    
    if all_match:
        print("✓ All tables migrated successfully!")
    else:
        print("✗ Some tables have mismatched counts!")
    
    vercel_cur.close()
    cloud_cur.close()
    vercel_conn.close()
    cloud_conn.close()

if __name__ == '__main__':
    validate_migration()
```

## Troubleshooting

### Error: "role does not exist"
```sql
-- Create the role on the new database
CREATE ROLE default WITH LOGIN PASSWORD 'password';
```

### Error: "database does not exist"
```sql
-- Create the database
CREATE DATABASE verceldb;
```

### Error: "SSL connection required"
```bash
# Add sslmode=require to connection string
psql "postgres://user:pass@host/db?sslmode=require"
```

### Error: "password authentication failed"
- Verify credentials in Vercel dashboard
- Check that user has proper permissions
- Ensure IP is whitelisted (for cloud databases)

---

**Remember**: Always test the backup/restore process before you need it!
