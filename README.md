# UZNR Crne Gore

Website of the Association for Occupational Safety of Montenegro — *Udruženje
zaštite na radu Crne Gore*.

Two applications in one repository:

```
frontend/   Vue 3 + Vite    →  Netlify   https://uznr.netlify.app
backend/    Django + DRF    →  Render    API, media and the admin
```

The public site is Montenegrin and English; the admin is Montenegrin only,
because the people who use it are.

## Running it locally

Two terminals. The frontend expects the API on `localhost:8000`, which is the
default in `frontend/src/api.js`.

```sh
# backend
cd backend
python -m venv venv && venv/Scripts/activate    # or: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_seed                    # first run only
python manage.py runserver
```

```sh
# frontend
cd frontend
npm install
npm run dev
```

On Windows, start the backend with UTF-8 output. Without it the console mail
backend cannot print Montenegrin characters, and sending a contact confirmation
fails with `UnicodeEncodeError`:

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python manage.py runserver
```

## Deployment

Both services build from `master` in this repository, each looking only at its
own directory:

| | Config | Builds from |
| --- | --- | --- |
| Netlify | `netlify.toml` — `base = "frontend"` | `frontend/` |
| Render | `render.yaml` — `rootDir: backend` | `backend/` |

Both files sit at the repository root, which is where each platform looks for
them.

**Before running this as a real site, read [PRODUCTION.md](PRODUCTION.md).** The
short version: the free Render plan wipes the database on every deploy, the
admin password is in this repository, and e-mail may not be configured — all
three have to be settled first.

## Where things are

| Path | |
| --- | --- |
| `frontend/src/pages/` | one file per route |
| `frontend/src/components/` | shared UI |
| `frontend/src/i18n/locales/` | Montenegrin and English text |
| `frontend/src/data/` | bundled fallbacks, used while the API wakes up |
| `backend/content/models.py` | the content types the admin edits |
| `backend/content/admin.py` | admin layout, grouping and the home page |
| `backend/content/seed_data/` | initial content for a fresh database |
| `backend/templates/admin/` | admin template overrides |

The frontend renders from `src/data/` first and replaces it with the API
response once that arrives, so every page works while the backend is asleep.
