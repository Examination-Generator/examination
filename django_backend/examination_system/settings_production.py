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
if os.getenv('POSTGRES_URL'):
    print("Using POSTGRES_URL for database configuration", file=sys.stderr)
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=os.getenv('POSTGRES_URL'),
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        print(f"✓ Database configured successfully", file=sys.stderr)
    except Exception as e:
        print(f"✗ Database configuration failed: {e}", file=sys.stderr)
        raise
elif os.getenv('DATABASE_URL'):
    print("Using DATABASE_URL for database configuration", file=sys.stderr)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    print("⚠ No database URL found - using default from base settings", file=sys.stderr)

# Static files configuration for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS configuration for production
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all in debug mode
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Security settings - Vercel handles SSL, so we don't redirect
SECURE_SSL_REDIRECT = False  # Vercel handles this
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

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
