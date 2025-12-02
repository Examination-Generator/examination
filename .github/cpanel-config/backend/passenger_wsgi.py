#!/usr/bin/env python
"""
Passenger WSGI file for cPanel deployment
This file is automatically used by cPanel Python App to run Django
"""
import sys
import os
import logging

# Configure logging for startup diagnostics
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [PASSENGER] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("Starting Django application via Passenger WSGI")
logger.info(f"Python version: {sys.version}")
logger.info("Python executable: {sys.executable}")

# Add your project directory to the sys.path
# This must match where the code is deployed (public_html/api)
project_home = '/home/zbhxqeap/public_html/api'
logger.info(f"Project home: {project_home}")
logger.info(f"Current working directory: {os.getcwd()}")

if project_home not in sys.path:
    sys.path.insert(0, project_home)
    logger.info("✓ Project directory added to sys.path")

# Activate virtual environment created by cPanel Python App
# cPanel creates venv at /home/zbhxqeap/virtualenv/api/3.x/
venv_paths = [
    os.path.join(project_home, 'venv/bin/activate_this.py'),  # Manual venv
    '/home/zbhxqeap/virtualenv/api/3.12/bin/activate_this.py',  # cPanel Python 3.12
    '/home/zbhxqeap/virtualenv/api/3.11/bin/activate_this.py',  # cPanel Python 3.11
    '/home/zbhxqeap/virtualenv/api/3.13/bin/activate_this.py',  # cPanel Python 3.13
]

activated = False
for activate_this in venv_paths:
    if os.path.exists(activate_this):
        try:
            with open(activate_this) as file_:
                exec(file_.read(), dict(__file__=activate_this))
            logger.info(f"✓ Virtual environment activated: {activate_this}")
            activated = True
            break
        except Exception as e:
            logger.warning(f"⚠ Failed to activate {activate_this}: {e}")

if not activated:
    logger.info("ℹ No virtual environment found, using system Python")

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'examination_system.settings_production'
logger.info(f"✓ Django settings: {os.environ['DJANGO_SETTINGS_MODULE']}")

# Load environment variables from .env file (if exists)
env_file = os.path.join(project_home, '.env')
if os.path.exists(env_file):
    logger.info("Loading .env file...")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
    logger.info("✓ Environment variables loaded from .env")

try:
    # Import Django application
    from examination_system.wsgi import application
    logger.info("✓ Django WSGI application loaded successfully")
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"✗ FAILED to load Django application: {e}")
    logger.error("=" * 80)
    raise

# Make sure application is available at module level for Passenger
# (already imported above, this comment just documents the requirement)
