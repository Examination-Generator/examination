import sys
import os

# Add your project directory to the sys.path
project_home = '/home/zbhxqeap/public_html/api'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtual environment
activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'examination_system.settings_production'

# Import Django application
from examination_system.wsgi import application
