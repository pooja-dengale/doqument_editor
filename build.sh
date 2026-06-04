#!/usr/bin/env bash
# Render build script — runs automatically on every deploy
set -o errexit

export DJANGO_SETTINGS_MODULE=ajaia_docs.settings_prod

pip install -r requirements.txt

python manage.py migrate --settings=ajaia_docs.settings_prod

python manage.py collectstatic --no-input --settings=ajaia_docs.settings_prod

python manage.py seed_users --settings=ajaia_docs.settings_prod
