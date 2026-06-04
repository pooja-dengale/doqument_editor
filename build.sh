#!/usr/bin/env bash
# Render build script — runs automatically on every deploy
set -o errexit

pip install -r requirements.txt

# Apply database migrations
python manage.py migrate --settings=ajaia_docs.settings_prod

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input --settings=ajaia_docs.settings_prod

# Seed the three test users (safe to re-run — skips existing users)
python manage.py seed_users --settings=ajaia_docs.settings_prod
