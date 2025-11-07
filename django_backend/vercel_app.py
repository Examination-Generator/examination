#!/usr/bin/env python
"""
WSGI entry point for Vercel deployment with comprehensive error handling
This file is the entry point for Vercel serverless functions
"""
import os
import sys
import traceback
import json

print("=" * 80, file=sys.stderr)
print("VERCEL_APP.PY LOADING", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings_production')

# Global error handler to catch runtime errors
class ErrorCatchingWSGI:
    """WSGI middleware to catch and log all runtime errors"""
    
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
    
    def __call__(self, environ, start_response):
        try:
            return self.wsgi_app(environ, start_response)
        except Exception as e:
            # Log the error
            print("=" * 80, file=sys.stderr)
            print(f"✗ RUNTIME ERROR: {type(e).__name__}: {str(e)}", file=sys.stderr)
            print(f"Path: {environ.get('PATH_INFO')}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            # Return JSON error for API endpoints
            if environ.get('PATH_INFO', '').startswith('/api/'):
                error_data = {
                    'success': False,
                    'message': str(e),
                    'error': str(e),
                    'type': type(e).__name__,
                }
                response_body = json.dumps(error_data).encode('utf-8')
                status = '500 Internal Server Error'
                headers = [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(response_body))),
                    ('Access-Control-Allow-Origin', '*'),
                ]
                start_response(status, headers)
                return [response_body]
            else:
                # Return HTML error
                error_message = f"Error: {type(e).__name__}: {str(e)}"
                response_body = error_message.encode('utf-8')
                status = '500 Internal Server Error'
                headers = [('Content-Type', 'text/plain')]
                start_response(status, headers)
                return [response_body]

try:
    # Import Django WSGI application
    from django.core.wsgi import get_wsgi_application
    
    print("Initializing Django WSGI application...", file=sys.stderr)
    django_application = get_wsgi_application()
    
    # Wrap with error handler
    application = ErrorCatchingWSGI(django_application)
    app = application
    
    print("✓ Django initialized successfully!", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
except Exception as e:
    # Print detailed error for debugging
    print("=" * 80, file=sys.stderr)
    print(f"✗ INITIALIZATION ERROR: {type(e).__name__}: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Create a simple error app that returns JSON for API routes
    def app(environ, start_response):
        # Return JSON for API endpoints
        if environ.get('PATH_INFO', '').startswith('/api/'):
            error_data = {
                'success': False,
                'message': f'Django initialization failed: {str(e)}',
                'error': str(e),
                'type': type(e).__name__,
            }
            response_body = json.dumps(error_data).encode('utf-8')
            status = '500 Internal Server Error'
            headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body))),
                ('Access-Control-Allow-Origin', '*'),
            ]
        else:
            error_msg = f"Django initialization failed: {str(e)}"
            response_body = error_msg.encode('utf-8')
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/plain')]
        
        start_response(status, headers)
        return [response_body]
