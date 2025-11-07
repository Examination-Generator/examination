"""
WSGI config for examination_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings')

application = get_wsgi_application()

# Vercel compatibility
app = application
