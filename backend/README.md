# UZNR backend

Django + Django REST Framework backend for the UZNR site. Django's built-in
admin (`/admin/`) is the CMS — staff log in there to add/edit news posts and
members, including uploading thumbnail/logo images directly. The public API
(read-only) is what the Vue frontend consumes.

`content/seed_data/*.json` holds the news/members content originally scraped
from uznr.me. `python manage.py import_seed` loads it into the database and
downloads the real images into `media/` — safe to re-run, it skips images
that already exist.

## Setup

Windows:
```
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py import_seed
venv\Scripts\python.exe manage.py createsuperuser
```

Linux/WSL:
```
python3 -m venv venv_linux
source venv_linux/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_seed
python manage.py createsuperuser
```

## Run

Windows: `venv\Scripts\python.exe manage.py runserver 8000`
Linux/WSL: `python manage.py runserver 8000`

- Public API: http://localhost:8000/api/
- Admin/CMS: http://localhost:8000/admin/

## Endpoints

- `GET /api/health`
- `GET /api/news` — list news, newest first
- `GET /api/news/{slug}` — single news item
- `GET /api/members` — list association members
- `GET /api/announcements` — Oglasi
- `GET /api/important-links`
- `GET /api/pages/{slug}` — editable content for one page (see below)
- `POST /api/contact` — contact form submission (the only write endpoint)

Everything else is read-only by design: news, members and page content are
edited in `/admin/`, not through the API.

## Page content (CMS)

`/admin/` → **Stranice** holds the editable content of the site's pages:

- **Stranica** — one page, matched to the frontend route by its slug
  (`regulativa` → `/regulativa`).
- **Sekcija** — a block within a page: `Tekst`, `Linkovi`, `Dokumenti`,
  `Galerija fotografija` or `Pitanja i odgovori`. Sections can be reordered and
  hidden without deleting them.
- **Stavka** — one link, document, photo or Q&A pair inside a section. A link
  is either an external address (`https://…`) or a path to a document the
  frontend already publishes (`/documents/regulativa/zakon.pdf`), or an upload,
  which lands in `media/` and has its size filled in automatically.

Every text field exists twice, Montenegrin and English (`… (EN)`). A blank
English field falls back to the Montenegrin one, so the EN site is never empty.

`GET /api/pages/{slug}` returns both languages for each field
(`{"mne": "…", "en": "…"}`); the frontend picks one without refetching when the
visitor switches language.

Pages currently wired to the frontend: `regulativa`, `publikacije`, `press`,
`pitanja-odgovori`. The frontend keeps a bundled copy of that content and falls
back to it whenever the API is unreachable or a page has no sections, so a
sleeping backend never blanks out a page.

`python manage.py import_pages` seeds these pages from
`content/seed_data/pages/*.json`. It skips pages that already exist; pass
`--replace <slug>` to reload one deliberately. The JSON is generated from the
frontend by `node scripts/export-page-content.mjs` (run there, not here).

## Translations

The English text lives in the same seed files as the Montenegrin, in `*_en`
keys, so a fresh database is bilingual the moment it is seeded. A database
seeded *before* a translation was written stays Montenegrin-only, because the
import commands only write English on rows they create. `python manage.py
import_translations` fixes that: it re-reads the seed files and copies across
nothing but the `*_en` fields, matching rows by their Montenegrin text. It is
safe to re-run, and it leaves an English field that already has something in it
alone — pass `--overwrite` to replace admin edits, or `--dry-run` to look first.

Document titles are deliberately left in Montenegrin: laws, rulebooks and
publications are cited by their official names. Their small print (the gazette
reference) is translated, as are the headings of the groups they sit in.

## Contact form

`POST /api/contact` with JSON:

```json
{"name": "…", "email": "…", "phone": "", "organisation": "",
 "subject": "general|membership|exam|cooperation|media",
 "message": "…", "language": "mne|en", "website": ""}
```

- The message is saved first, then two e-mails go out: a confirmation to the
  sender (in the language they were reading) and a notification to
  `CONTACT_NOTIFY_EMAILS` whose Reply-To is the sender.
- Mail failures never fail the request. The message is already stored, and the
  admin list shows a red **Nije poslata** for any confirmation that did not go
  out — select it and run **Ponovo pošalji potvrdu pošiljaocu**.
- `website` is a honeypot. Filled in, the submission is dropped and still
  answered `201` so bots learn nothing.
- Throttled to `CONTACT_THROTTLE_RATE` (default `5/hour`) per IP.
- Messages arrive under **Poruke sa sajta**. They cannot be created or edited
  there — only the status and the internal note are editable.

### E-mail configuration

Set on Render (see `render.yaml`):

| Variable | Meaning |
| --- | --- |
| `EMAIL_HOST` | SMTP server. **Unset → mail is printed to the log, not sent.** |
| `EMAIL_PORT` / `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | Defaults: 587 / True / False |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials |
| `DEFAULT_FROM_EMAIL` | Must be an address the SMTP account may send as |
| `CONTACT_NOTIFY_EMAILS` | Comma-separated recipients of the office copy |
| `CONTACT_OFFICE_EMAIL`, `CONTACT_OFFICE_PHONE` | Shown in the mail footer |
| `SITE_URL`, `BACKEND_URL` | Used for links inside the e-mails |

### Testing the e-mail

Two layers, both worth running after changing anything about mail:

1. **Automated** — `python manage.py test content` covers the endpoint,
   validation, the honeypot, the throttle, both languages of the confirmation,
   the Reply-To headers, and that a message survives a dead mail server. No
   credentials or network needed.
2. **Live** — `python manage.py send_test_email you@example.com` sends a real
   confirmation through the configured SMTP server and reports what happened.
   Add `--lang en` for the English version and `--notify` to also send the
   office copy. Nothing is stored unless you pass `--keep`. Run it once on
   Render after setting the credentials:
   `render ssh` → `python manage.py send_test_email you@example.com --notify`.

   With no `EMAIL_HOST` set it prints the message instead of sending, which is
   a quick way to preview the wording.
