"""
Production settings for Render deployment.
All secrets come from environment variables set in Render's dashboard.
"""
from .settings import *
import os
import dj_database_url

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

# Accepts comma-separated hosts, e.g. ".onrender.com,localhost"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '.onrender.com,localhost').split(',')]

# ── Database — Render injects DATABASE_URL automatically ─────────────────────
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ── Static files via WhiteNoise ───────────────────────────────────────────────
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── CORS — allow the Vercel frontend ─────────────────────────────────────────
# Set FRONTEND_URL in Render dashboard to your Vercel URL
CORS_ALLOWED_ORIGINS = [
    u.strip()
    for u in os.environ.get('FRONTEND_URL', 'http://localhost:3000').split(',')
]

# ── HTTPS / security headers ──────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
