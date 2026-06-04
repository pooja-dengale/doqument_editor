# AjaiaDoc — Collaborative Document Editor

A full-stack document editor built entirely with Django — server-rendered using Django Template Language (DTL), session authentication, and Quill.js for rich text editing.

## Live Demo

| | URL |
|---|---|
| **App** | https://ajaia-docs-api-dnt2.onrender.com |
| **GitHub** | https://github.com/pooja-dengale/doqument_editor |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14, Django 5, Django REST Framework |
| Templating | Django Template Language (DTL) |
| Rich Text | Quill.js 1.3.7 (via CDN) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Django session authentication |
| Hosting | Render |

---

## Project Structure

```
ajaia_docs/              ← Django project config
  settings.py            ← Development settings
  settings_prod.py       ← Production settings (Render)
  urls.py                ← All URL routes
  wsgi.py

editor/
  models.py              ← Document, DocumentShare
  dtl_views.py           ← All server-rendered views
  views.py               ← REST API views (kept for tests)
  serializers.py
  templates/editor/
    base.html            ← Base layout, CSS, Quill CDN
    login.html           ← Login page
    editor.html          ← Main editor UI
  management/commands/
    seed_users.py        ← Seeds Alice, Bob, Charlie
  tests.py               ← 9 passing tests

requirements.txt
build.sh                 ← Render build script
Procfile                 ← Gunicorn start command
render.yaml              ← Render deployment config
```

---

## Features

- **Login / logout** — Django session auth
- **Document list** — sidebar split into "My Documents" / "Shared with Me"
- **Rich text editor** — Quill.js (Bold, Italic, Underline, H1/H2, Lists)
- **File import** — Upload `.txt` or `.md`, parsed client-side via FileReader
- **Document sharing** — Grant `view` or `edit` access per user
- **Permission enforcement** — View-only users get a read-only editor; enforced server-side too
- **Share modal** — Owner can add/revoke users inline

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Seed test users (Alice, Bob, Charlie)
python manage.py seed_users

# Start server
python manage.py runserver
# → http://127.0.0.1:8000
```

**Test accounts:**
| User | Password |
|---|---|
| alice | alice1234 |
| bob | bob12345 |
| charlie | charlie1 |

---

## Running Tests

```bash
python manage.py test editor -v 2
# 9 tests — all passing
```

---

## Deployment (Render)

```bash
# Build command (set in Render dashboard or render.yaml)
chmod +x build.sh && ./build.sh

# Start command
DJANGO_SETTINGS_MODULE=ajaia_docs.settings_prod gunicorn ajaia_docs.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Required environment variables on Render:**
| Key | Value |
|---|---|
| `SECRET_KEY` | any long random string |
| `ALLOWED_HOSTS` | `ajaia-docs-api-dnt2.onrender.com,.onrender.com` |
| `DATABASE_URL` | PostgreSQL Internal URL (optional, falls back to SQLite) |
