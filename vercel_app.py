import os
import sys

# Add Django project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'django_backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()  # Vercel needs it named 'app'
