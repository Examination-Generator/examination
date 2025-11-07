"""
Production settings for Vercel deployment
"""
import os
import dj_database_url
from .settings import *

# Security settings for production
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'temporary-secret-key-change-in-production')

# Vercel-specific hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '.vercel.app').split(',')

# Database configuration for Vercel Postgres
if os.getenv('POSTGRES_URL'):
    # Use Vercel Postgres URL directly
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('POSTGRES_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

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
LOGGING['root']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'
