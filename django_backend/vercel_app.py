#!/usr/bin/env python
"""
WSGI entry point for Vercel deployment
"""
import os
from django.core.wsgi import get_wsgi_application

# Use production settings on Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')

application = get_wsgi_application()

# Vercel requires the WSGI application to be exported as 'app'
app = application
