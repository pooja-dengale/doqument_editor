"""
Production settings for Render deployment.
Extends base settings.py and overrides with production-safe values.
All secrets are read from environment variables set in Render's dashboard.
"""
from .settings import *
import os
import dj_database_url

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ── Database — Render provides DATABASE_URL automatically ────────────────────
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Static files served by WhiteNoise ────────────────────────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── CORS — allow the Vercel frontend domain ───────────────────────────────────
# Set FRONTEND_URL in Render dashboard, e.g. https://doqument-editor.vercel.app
CORS_ALLOWED_ORIGINS = os.environ.get(
    'FRONTEND_URL', 'http://localhost:3000'
).split(',')

# ── Security headers ─────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
