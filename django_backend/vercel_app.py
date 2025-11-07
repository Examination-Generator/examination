#!/usr/bin/env python
"""
WSGI entry point for Vercel deployment
This file is the entry point for Vercel serverless functions
"""
import os
import sys
import traceback

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')

try:
    # Import Django WSGI application
    from django.core.wsgi import get_wsgi_application
    
    # Initialize Django
    application = get_wsgi_application()
    
    # Vercel requires the WSGI application to be exported as 'app'
    app = application
    
except Exception as e:
    # Print detailed error for debugging
    print(f"Error initializing Django application: {str(e)}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    
    # Create a simple error app
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        error_msg = f"Django initialization failed: {str(e)}\n\n{traceback.format_exc()}"
        return [error_msg.encode('utf-8')]
