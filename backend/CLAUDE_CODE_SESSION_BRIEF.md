# Project Brief: UZNR Website Rebuild

**For:** Claude Code (VS Code extension)
**Context:** This brief summarizes a planning conversation. Paste this into a new Claude Code session in your project folder to continue.

---

## 1. What this is

A full custom rebuild of **https://uznr.me/** — the website for *Udruženje zaštite na radu Crne Gore* (the Occupational Safety and Health Association of Montenegro), a nonprofit/professional association.

The current site is built on **WordPress** (Site Kit by Google, standard WP structure). We are moving **off WordPress entirely** to a custom-built site.

## 2. Tech stack (confirmed)

- **Frontend:** Vue 3 + Vite
- **Backend:** Python (framework not yet chosen — recommend Flask or FastAPI, lean toward FastAPI for a cleaner API + auto docs if a CMS/admin panel gets built later)
- **Note:** An earlier scaffold (`Test1.7z`, containing a `frontend/` folder and a `proba/` folder) was checked and found to be **empty boilerplate only** — the default Vue+Vite starter template with no custom code, and an empty Python venv with no application code. Nothing from that archive needs to be preserved or migrated; it only confirmed the intended stack. Start fresh.

## 3. Scope

**Full multi-page custom rebuild**, not just a homepage mockup. Priority pages to be defined at build time, but the current site's structure (for reference) is:

- Početna (Home)
- O nama (About us)
- Regulativa (Regulations)
- Projekti (Projects)
- Oglasi (Announcements/Listings)
- Publikacije (Publications)
- Biblioteka (Library) — with sub-pages: Stručni ispit, EU Osha, No time to lose, Dokumenta
- Press/Media
- Pitanja & Odgovori (Q&A)
- Arhiva (Archive)
- Kontakt (Contact)

## 4. Current site content inventory (from live crawl of uznr.me)

- **Header:** logo, contact info (email/phone), live clock widget, search
- **Hero section:** org name/tagline, "O nama" CTA button
- **4 feature blocks:** Ciljevi (Goals), Vizija (Vision), Saradnja (Cooperation), Edukacija (Education)
- **Novosti (News) feed:** repeating list of news posts with thumbnail, title, excerpt, date, "Opširnije" (read more) link. This is the most actively updated content — posts appear roughly weekly/monthly covering conferences, workshops, project meetings.
- **Embedded YouTube video**
- **"Važni linkovi" (Important links) block:** PDF downloads (authorized organizations list, coordinators list), ministry links, posters/flyers, campaign materials, partner org logos (EU-OSHA, ILO, IOSH, ENETOSH, project-balcanosh.net)
- **"Najnovije" (Latest) sidebar:** duplicate/condensed news list
- **Weather widget** (Podgorica)
- **"Članovi Udruženja" (Association Members):** ~40+ member organizations, currently displayed as bare unstyled URLs with no logos/branding — flagged as a clear improvement opportunity
- **Footer:** "Ko smo mi" (who we are) blurb, address, contact, working hours, partner logos, copyright, "Web design: AstraWeb" credit
- **Login widget** (WordPress admin login — likely not needed in the rebuid unless a CMS/admin panel is built)

## 5. Known issues with current site (design rationale)

- Visually cluttered — repeated placeholder logo images used as generic icons
- Deep, crowded navigation (Biblioteka has 4 nested sub-items)
- No visual hierarchy in the news feed — long uniform list
- Member list (~40 orgs) shown as raw text links, no logos or cards — weakest visual section of the site
- Heavy widget stacking in sidebar/footer (duplicated content: news list appears twice, PDF links appear twice)
- Language: site is in Montenegrin/Serbian (Latin script) — rebuild should preserve this, no indication of needing translation/i18n

## 6. Content management (decision pending)

**Not yet decided:** who will manage content going forward (news posts, member list, PDF uploads) and how technical they are. This affects whether we need:

- A full admin panel/CMS (if non-technical staff will manage it), or
- Simple file/code-based content editing (if it's just the site owner editing directly)

**Action item:** Revisit this decision before finalizing backend architecture — it significantly affects whether the Python backend needs a database + auth + admin UI, or can be a simpler static-content-serving API.

## 7. Suggested next steps for Claude Code session

1. Scaffold a fresh Vue 3 + Vite frontend (ignore the old `Test1.7z` scaffold — start clean)
2. Scaffold a Python backend (recommend FastAPI) — keep minimal until the CMS decision above is resolved
3. Build homepage first: hero, 4 feature blocks, news feed (cleaned up), members section (redesigned as cards/logos instead of bare links), footer
4. Establish a design system early (colors, type, spacing) before building out remaining pages — the current site has no clear visual identity beyond a green/safety color scheme, which could be leaned into more deliberately
5. Once CMS decision is made, wire up news/content data (static JSON initially is fine, swap for DB-backed API later if needed)

---

*This brief was generated from a planning conversation on 2026-08-12 and reflects decisions made up to that point. Some details (exact page priority order, CMS requirements, hosting) are still open and should be confirmed with the site owner as work progresses.*
