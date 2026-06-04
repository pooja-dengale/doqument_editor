"""
WSGI config for ajaia_docs project.

Automatically uses production settings when running on Render
(detected via the RENDER environment variable that Render injects).
"""

import os

from django.core.wsgi import get_wsgi_application

# Render injects RENDER=true into every service automatically.
# This ensures production settings are always used on Render even if
# DJANGO_SETTINGS_MODULE is not explicitly set in the dashboard.
if os.environ.get('RENDER'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ajaia_docs.settings_prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ajaia_docs.settings')

application = get_wsgi_application()
