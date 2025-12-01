"""
Production settings for Vercel deployment
"""
import os
import sys

# Print diagnostic info
print("=" * 80, file=sys.stderr)
print("DJANGO PRODUCTION SETTINGS LOADING", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Environment variables:", file=sys.stderr)
print(f"  POSTGRES_URL: {'set' if os.getenv('POSTGRES_URL') else 'NOT SET'}", file=sys.stderr)
print(f"  SECRET_KEY: {'set' if os.getenv('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
print(f"  DEBUG: {os.getenv('DEBUG', 'NOT SET')}", file=sys.stderr)
print("=" * 80, file=sys.stderr)

try:
    import dj_database_url
    print("✓ dj_database_url imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"✗ Failed to import dj_database_url: {e}", file=sys.stderr)
    raise

try:
    from .settings import *
    print("✓ Base settings imported successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ Failed to import base settings: {e}", file=sys.stderr)
    raise

# Add auto-migration middleware at the beginning of MIDDLEWARE
# This ensures database is automatically set up on first request
MIDDLEWARE = [
    'api.middleware.AutoMigrateMiddleware',  # AUTO-MIGRATE: Run migrations automatically
] + MIDDLEWARE

# Security settings for production
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'temporary-secret-key-change-in-production')

print(f"DEBUG mode: {DEBUG}", file=sys.stderr)

# Vercel-specific hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '.vercel.app').split(',')
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}", file=sys.stderr)

# Database configuration for Vercel Postgres
# CRITICAL: Check for Vercel Postgres environment variables
postgres_url = (
    os.getenv('POSTGRES_URL') or 
    os.getenv('DATABASE_URL') or
    os.getenv('POSTGRES_PRISMA_URL') or
    os.getenv('POSTGRES_URL_NON_POOLING')
)

if postgres_url:
    print(f"✓ Found database URL (length: {len(postgres_url)} chars)", file=sys.stderr)
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=postgres_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        print(f"✓ Database configured successfully", file=sys.stderr)
        print(f"  Host: {DATABASES['default'].get('HOST', 'unknown')}", file=sys.stderr)
        print(f"  Port: {DATABASES['default'].get('PORT', 'unknown')}", file=sys.stderr)
        print(f"  Database: {DATABASES['default'].get('NAME', 'unknown')}", file=sys.stderr)
    except Exception as e:
        print(f"✗ Database configuration failed: {e}", file=sys.stderr)
        raise
else:
    # NO DATABASE URL FOUND - This is critical!
    print("=" * 80, file=sys.stderr)
    print("✗ CRITICAL ERROR: NO DATABASE URL ENVIRONMENT VARIABLE FOUND!", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("Please set one of these environment variables on Vercel:", file=sys.stderr)
    print("  - POSTGRES_URL (recommended)", file=sys.stderr)
    print("  - DATABASE_URL", file=sys.stderr)
    print("  - POSTGRES_PRISMA_URL", file=sys.stderr)
    print("  - POSTGRES_URL_NON_POOLING", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Use a dummy configuration that will fail gracefully
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'NOT_CONFIGURED',
            'USER': 'NOT_CONFIGURED',
            'PASSWORD': 'NOT_CONFIGURED',
            'HOST': 'NOT_CONFIGURED',
            'PORT': '5432',
        }
    }
    print("⚠ Using dummy database config - app will not work until POSTGRES_URL is set", file=sys.stderr)

# Static files configuration for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS configuration for production
# Allow all origins for Vercel deployments (both frontend and backend are on .vercel.app)
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for flexible Vercel deployments
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
] + CORS_ALLOWED_ORIGINS

CORS_ALLOW_CREDENTIALS = True

# Security settings - Vercel handles SSL, so we don't redirect
SECURE_SSL_REDIRECT = False  # Vercel handles this
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow iframes from same origin for previews

# Internationalization (ensure TIME_ZONE is set for production)
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Logging for production
LOGGING['handlers']['file'] = {
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}
LOGGING['root']['level'] = 'DEBUG' if DEBUG else 'INFO'
LOGGING['loggers']['django']['level'] = 'DEBUG' if DEBUG else 'INFO'

print("=" * 80, file=sys.stderr)
print("DJANGO PRODUCTION SETTINGS LOADED SUCCESSFULLY", file=sys.stderr)
print("=" * 80, file=sys.stderr)
