# UZNR — Frontend

Vue 3 + Vite frontend for Udruženje zaštite na radu Crne Gore.

## Local development

```sh
npm install
npm run dev
```

The dev server proxies nothing; API calls go straight to the URL in
`VITE_API_BASE_URL`, falling back to `http://localhost:8000` (see `src/api.js`).

## Deployment

Deploys are automatic. Pushing to `master` on
[jovanpop02/uznr-frontend](https://github.com/jovanpop02/uznr-frontend)
triggers a Netlify build of https://uznr.netlify.app — no manual
`netlify deploy` step is needed.

Build settings live in `netlify.toml`. SPA routing is handled by
`public/_redirects`, which Vite copies into `dist/` at build time.

The production API base URL is committed in `.env.production`, so the build
needs no environment variables configured on Netlify.

## Contact form

The form on `/kontakt` (`src/components/ContactForm.vue`) POSTs to the Django
backend at `POST /api/contact`. The backend stores the message, e-mails a
confirmation to the sender and forwards a copy to the Association — see the
backend README for the e-mail configuration and how to test it.

The form needs the backend running: with `npm run dev` that means Django on
`http://localhost:8000` (or whatever `VITE_API_BASE_URL` points at). A failed
request leaves the form in its error state with the address to write to
instead; a `429` shows the "too many messages" message rather than the generic
one.

## Editable page content

`regulativa`, `publikacije`, `press` and `pitanja-odgovori` render content from
the backend's CMS (`GET /api/pages/{slug}`, see `src/cms.js`). Each of those
pages still imports its list from `src/data/` and uses it as a fallback, so the
page renders instantly and survives the backend being asleep or unreachable —
the API result replaces it once it lands.

`scripts/export-page-content.mjs` regenerates the backend's seed JSON from
those `src/data/` files. It is only needed when seeding a fresh database; once
content is edited in the admin, the database is the source of truth and
re-seeding would discard those edits (`import_pages` skips existing pages
unless told otherwise).

## Backend

The API is a Django app deployed on Render's free tier, which spins down after
~15 minutes of inactivity. The first request after an idle period waits for a
cold start, so news and announcements can take up to a minute to appear.
