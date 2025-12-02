#!/usr/bin/env python
import sys
import os

# Add project to path
sys.path.insert(0, '/home/zbhxqeap/public_html/api')

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'examination_system.settings_production'

# Import application
from examination_system.wsgi import application
