# AjaiaDoc — Lightweight Collaborative Document Editor

A full-stack document editor with real-time rich-text editing, file import, and per-user document sharing.

## Live Demo

| | URL |
|---|---|
| **Frontend** | https://ajaia-docs-bay.vercel.app |
| **Backend API** | https://ajaia-docs-api-dnt2.onrender.com/api/ |



| Layer | Technology |
|---|---|
| Backend | Python 3.14, Django 5, Django REST Framework |
| Database | SQLite (dev) |
| Frontend | React 19, Vite, ReactQuill (react-quill-new), Axios |
| Auth | DRF Token Authentication |

---

## Project Structure

```
ajaia_docs/        ← Django project config (settings, urls, wsgi)
editor/            ← Django app (models, views, serializers, tests)
  migrations/      ← Database migrations
  management/      ← seed_users management command
frontend/          ← React + Vite application
  src/
    api.js                    ← Axios client + all API calls
    App.jsx                   ← Root state manager
    components/
      Header.jsx              ← Nav + user switcher
      Sidebar.jsx             ← Document list (My Docs / Shared with Me) + Import
      EditorPane.jsx          ← ReactQuill editor + Save + Share button
      ShareModal.jsx          ← Grant/revoke access modal
requirements.txt   ← Python dependencies
```

---

## Local Development

### 1. Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Seed test users (Alice, Bob, Charlie)
python manage.py seed_users

# Start Django dev server
python manage.py runserver
# → http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| POST | `/api/auth/token/` | Obtain auth token |
| GET | `/api/documents/` | List accessible documents |
| POST | `/api/documents/` | Create document |
| GET | `/api/documents/{id}/` | Retrieve document |
| PATCH | `/api/documents/{id}/` | Update document |
| DELETE | `/api/documents/{id}/` | Delete document |
| POST | `/api/documents/{id}/share/` | Share with a user |
| DELETE | `/api/documents/{id}/share/{username}/` | Revoke access |
| GET | `/api/users/` | List all users |

---

## Features

- **Rich text editing** — Bold, Italic, Underline, Headings, Lists via Quill
- **File import** — Upload `.txt` or `.md` files; parsed client-side via `FileReader`
- **Document sharing** — Grant `view` or `edit` access per user
- **Permission enforcement** — View-only users get a read-only editor; backend enforces on every request
- **Mock auth switcher** — Switch between Alice, Bob, Charlie to test sharing flows

---

## Running Tests

```bash
python manage.py test editor -v 2
# 9 tests — all passing
```

---

## Deployment Notes

For production deployment:
- Replace SQLite with PostgreSQL
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Use environment variables for `SECRET_KEY`
- Build the frontend: `cd frontend && npm run build`
- Serve the Django app with Gunicorn behind Nginx
- Serve the React `dist/` folder as static files or deploy to Vercel/Netlify
