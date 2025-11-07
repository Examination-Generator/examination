#!/usr/bin/env python
"""
WSGI entry point for Vercel deployment
This file is the entry point for Vercel serverless functions
"""
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Initialize Django
application = get_wsgi_application()

# Vercel requires the WSGI application to be exported as 'app'
app = application
