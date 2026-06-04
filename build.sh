#!/usr/bin/env bash
# Render build script — RENDER env var is always set by Render automatically,
# so manage.py and wsgi.py will auto-select settings_prod.
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py seed_users
