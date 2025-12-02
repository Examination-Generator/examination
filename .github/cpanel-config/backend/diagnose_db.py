"""
Database connection diagnostic script
Run this in cPanel Python App "Execute python script" to find the correct database settings
"""
import os
import sys

print("=" * 80)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 80)
print()

# Show environment variables
print("Environment Variables:")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"  DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
print()

# Try different connection methods
import psycopg2

connection_attempts = [
    {
        'name': 'Unix socket (empty host)',
        'params': {
            'dbname': 'zbhxqeap_exam',
            'user': 'zbhxqeap_editor',
            'password': 'TesterK&700',
            'host': '',  # Unix socket
        }
    },
    {
        'name': 'localhost',
        'params': {
            'dbname': 'zbhxqeap_exam',
            'user': 'zbhxqeap_editor',
            'password': 'TesterK&700',
            'host': 'localhost',
        }
    },
    {
        'name': '127.0.0.1',
        'params': {
            'dbname': 'zbhxqeap_exam',
            'user': 'zbhxqeap_editor',
            'password': 'TesterK&700',
            'host': '127.0.0.1',
        }
    },
    {
        'name': 'localhost with port 5432',
        'params': {
            'dbname': 'zbhxqeap_exam',
            'user': 'zbhxqeap_editor',
            'password': 'TesterK&700',
            'host': 'localhost',
            'port': '5432',
        }
    },
]

print("Testing database connections...")
print()

successful_connection = None

for attempt in connection_attempts:
    print(f"Trying: {attempt['name']}")
    try:
        conn = psycopg2.connect(**attempt['params'])
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"  ✓ SUCCESS!")
        print(f"  PostgreSQL version: {version[:50]}...")
        print()
        successful_connection = attempt
        break
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}")
        print()

print("=" * 80)
if successful_connection:
    print("SUCCESSFUL CONNECTION FOUND!")
    print()
    print("Use these settings in your .env or environment variables:")
    print()
    for key, value in successful_connection['params'].items():
        if key == 'password':
            continue
        env_key = f"DB_{key.upper()}"
        print(f"  {env_key}={value}")
    print()
    print("Django DATABASES configuration:")
    print()
    print("DATABASES = {")
    print("    'default': {")
    print("        'ENGINE': 'django.db.backends.postgresql',")
    for key, value in successful_connection['params'].items():
        if key == 'password':
            continue
        django_key = key.upper() if key != 'dbname' else 'NAME'
        if django_key == 'NAME':
            key = 'dbname'
        print(f"        '{django_key}': '{value}',")
    print("        'PASSWORD': os.getenv('DB_PASSWORD'),")
    print("    }")
    print("}")
else:
    print("NO SUCCESSFUL CONNECTION FOUND!")
    print()
    print("Please check:")
    print("  1. PostgreSQL is running")
    print("  2. Database 'zbhxqeap_exam' exists")
    print("  3. User 'zbhxqeap_editor' has access permissions")
    print("  4. Password is correct")
    print()
    print("Contact your hosting provider to verify PostgreSQL configuration.")

print("=" * 80)
