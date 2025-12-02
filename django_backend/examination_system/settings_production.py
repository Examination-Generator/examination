"""
Production settings - Environment-aware configuration
Automatically detects and configures for: Vercel (staging) or cPanel (production)
"""
import os
import sys

# Detect environment
def get_environment():
    """Detect if running on Vercel or cPanel"""
    if os.getenv('VERCEL'):
        return 'vercel'
    elif os.path.exists('/home/zbhxqeap'):  # cPanel specific path
        return 'cpanel'
    return 'local'

ENVIRONMENT = get_environment()

# Print diagnostic info
print("=" * 80, file=sys.stderr)
print(f"DJANGO SETTINGS - ENVIRONMENT: {ENVIRONMENT}", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print("=" * 80, file=sys.stderr)

try:
    from .settings import *
    print("✓ Base settings imported successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to import base settings: {e}", file=sys.stderr)
    raise

# Environment-specific configuration
if ENVIRONMENT == 'vercel':
    # Vercel staging environment
    try:
        import dj_database_url
        print("✓ dj_database_url imported (Vercel)", file=sys.stderr)
    except ImportError as e:
        print(f"✗ Failed to import dj_database_url: {e}", file=sys.stderr)
        raise
    
    # Add auto-migration middleware for Vercel
    MIDDLEWARE = ['api.middleware.AutoMigrateMiddleware'] + MIDDLEWARE
    
    ALLOWED_HOSTS = ['.vercel.app', 'examination-s3np.vercel.app']
    
    # Vercel Postgres database
    postgres_url = (
        os.getenv('POSTGRES_URL') or 
        os.getenv('POSTGRES_URL_NON_POOLING') or
        os.getenv('DATABASE_URL') or
        os.getenv('POSTGRES_PRISMA_URL')
    )
    
    if postgres_url:
        DATABASES = {
            'default': dj_database_url.config(
                default=postgres_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        print(f"✓ Vercel database configured", file=sys.stderr)
    else:
        print("✗ No Vercel database URL found!", file=sys.stderr)
    
    CORS_ALLOWED_ORIGINS = [
        'https://examination-2hhl.vercel.app',
        'https://examination-s3np.vercel.app'
    ]
    
elif ENVIRONMENT == 'cpanel':
    # cPanel production environment
    
    # Add auto-migration middleware for cPanel
    MIDDLEWARE = ['api.middleware.AutoMigrateMiddleware'] + MIDDLEWARE
    
    ALLOWED_HOSTS = ['speedstarexams.co.ke', '51.91.24.182', 'www.speedstarexams.co.ke']
    
    # cPanel PostgreSQL database - reads from environment variables
    # cPanel typically uses the main cPanel username for PostgreSQL access
    db_host = os.getenv('DB_HOST', '')  # Empty string = Unix socket
    db_config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'zbhxqeap_exam'),
        'USER': os.getenv('DB_USER', 'zbhxqeap'),  # Try cPanel username
        'PASSWORD': os.getenv('DB_PASSWORD', ''),  # Empty = use system auth
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
    
    # Only add HOST and PORT if specified (otherwise use Unix socket)
    if db_host:
        db_config['HOST'] = db_host
        db_config['PORT'] = os.getenv('DB_PORT', '5432')
    
    DATABASES = {'default': db_config}
    
    print(f"✓ cPanel database configured: {DATABASES['default']['NAME']}", file=sys.stderr)
    print(f"  Connection method: {'Unix socket' if not db_host else f'TCP to {db_host}'}", file=sys.stderr)
    
    CORS_ALLOWED_ORIGINS = [
        'https://speedstarexams.co.ke',
        'https://www.speedstarexams.co.ke'
    ]
    
    # Static files for cPanel
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'
    
else:
    # Local development
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
    print("✓ Local development mode", file=sys.stderr)

# Common production settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'temporary-secret-key-change-in-production')

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all in debug mode
CORS_ALLOW_CREDENTIALS = True

# Security settings (only in production)
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Handled by reverse proxy
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

print(f"✓ Configuration complete - DEBUG: {DEBUG}", file=sys.stderr)
print("=" * 80, file=sys.stderr)
