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

# ── Database — use DATABASE_URL if set (Postgres), otherwise SQLite ───────────
import os as _os
_db_url = _os.environ.get('DATABASE_URL', '')
if _db_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=_db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite when no Postgres DB is attached (free Render plan)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
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
