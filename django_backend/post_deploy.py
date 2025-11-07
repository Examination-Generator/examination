#!/usr/bin/env python
"""
Post-deployment script to ensure database is initialized
This runs automatically after deployment to set up the database
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.core.management import call_command
from django.db import connection

def check_database():
    """Check if database is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def run_migrations():
    """Run all pending migrations"""
    try:
        print("\n" + "=" * 60)
        print("RUNNING DATABASE MIGRATIONS")
        print("=" * 60)
        
        call_command('migrate', '--noinput', verbosity=2)
        
        print("=" * 60)
        print("✓ MIGRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
        return True
    except Exception as e:
        print(f"\n✗ Migration failed: {e}\n")
        return False

def verify_tables():
    """Verify that required tables exist"""
    try:
        from api.models import User
        user_count = User.objects.count()
        print(f"✓ Tables verified. Users in database: {user_count}")
        return True
    except Exception as e:
        print(f"✗ Table verification failed: {e}")
        return False

def main():
    """Main post-deployment setup"""
    print("\n" + "=" * 60)
    print("POST-DEPLOYMENT SETUP STARTING")
    print("=" * 60 + "\n")
    
    # Step 1: Check database connection
    if not check_database():
        print("\n⚠️  WARNING: Database not accessible!")
        print("Make sure POSTGRES_URL environment variable is set.")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        print("\n⚠️  WARNING: Migrations failed!")
        sys.exit(1)
    
    # Step 3: Verify tables
    if not verify_tables():
        print("\n⚠️  WARNING: Table verification failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ POST-DEPLOYMENT SETUP COMPLETED SUCCESSFULLY")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
