#!/bin/bash
# Build script for Vercel deployment

# Install dependencies
pip install -r requirements.txt

# Collect static files (suppress errors if no static files)
python manage.py collectstatic --no-input --clear || true
