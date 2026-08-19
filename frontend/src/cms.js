/**
 * Reads admin-editable page content from the backend.
 *
 * Every page that uses this keeps its bundled copy of the content in
 * `src/data/` as a fallback. The API is the source of truth when it answers,
 * but the backend sleeps on Render's free tier and can take the better part of
 * a minute to wake — a visitor must never see an empty Regulations page while
 * that happens, so the bundled data renders immediately and is replaced once
 * the fetch lands.
 *
 * Text fields arrive as `{ mne, en }`; `text()` picks the active language.
 */

import { computed, ref } from 'vue'
import { fetchPage } from './api'

export function text(field, locale) {
  if (!field) return ''
  if (typeof field === 'string') return field
  return (locale === 'en' ? field.en : field.mne) || field.mne || ''
}

/** True for the `{ mne, en }` shape the API sends for translatable text. */
function isLocalized(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value) && 'mne' in value
}

/**
 * Resolves every `{ mne, en }` field in an API object down to a plain string
 * for the active language, leaving everything else alone.
 *
 * News, announcements and important links grew English fields after their
 * components were written, and those components read `item.title` as a string
 * in a dozen places. Resolving here keeps the templates as they were and keeps
 * one place responsible for the choice — and because callers wrap it in a
 * computed, switching language still re-renders without refetching.
 *
 * Bundled fallback content in `src/data/` is plain strings; those pass through
 * untouched, so a page still renders when the backend is asleep.
 */
export function localizeItem(item, locale) {
  if (Array.isArray(item)) return item.map((entry) => localizeItem(entry, locale))
  if (isLocalized(item)) return text(item, locale)
  if (item === null || typeof item !== 'object') return item

  const resolved = {}
  for (const [key, value] of Object.entries(item)) {
    resolved[key] = localizeItem(value, locale)
  }
  return resolved
}

/** localizeItem over a list. */
export function localizeList(items, locale) {
  return Array.isArray(items) ? items.map((item) => localizeItem(item, locale)) : []
}

/**
 * Fetches one page's sections. Returns a ref that stays null until the content
 * arrives, and stays null forever if the request fails — callers treat null as
 * "use the bundled data".
 */
export function usePageSections(slug) {
  const sections = ref(null)

  fetchPage(slug)
    .then((page) => {
      // An empty page in the admin should not blank out the site; that is far
      // more likely to be a half-finished edit than a deliberate deletion.
      if (page?.sections?.length) sections.value = page.sections
    })
    .catch(() => {
      // Falling back to the bundled content is the whole point — a backend that
      // is down or asleep must not break a content page.
    })

  return sections
}

/** Maps a CMS document/link item onto the shape the page components expect. */
export function toDocument(item, locale) {
  return {
    title: text(item.title, locale),
    reference: text(item.reference, locale),
    description: text(item.description, locale),
    file: item.href || '',
    pages: item.pages ?? null,
    sizeKb: item.size_kb ?? null,
    dateLabel: item.date_label || '',
  }
}

/**
 * Chooses between CMS sections and bundled data, and maps whichever wins.
 * `mapper` receives the raw CMS sections; `fallback` is returned untouched.
 */
export function withFallback(sections, fallback, mapper) {
  return computed(() => (sections.value ? mapper(sections.value) : fallback))
}

/* ---------------------------------------------------------------------------
 * Projects
 *
 * A project has more to it than a heading and a list of files — a period, a
 * duration, who funded it, who the partners were. The CMS stores a block's text
 * as one field, so those facts live as labelled lines at the top of it:
 *
 *     Period: 15.03.2022. – 14.03.2023.
 *     Trajanje: 12 mjeseci
 *     Finansira: Evropska unija …
 *     Partneri: NVO Prima (https://…), Fondacija …
 *
 *     <first paragraph>
 *
 * The import wrote that shape and this reads it back, so the page keeps its
 * chips and partner links while the text and documents stay editable in the
 * admin. Anything that is not a labelled line is treated as prose, which means
 * a block written by hand still renders — it simply has no chips.
 * ------------------------------------------------------------------------- */

const FACT_LABELS = {
  'Period': 'period',
  'Trajanje': 'duration',
  'Finansira': 'funding',
  'Nosilac': 'leadOrganization',
  'Partneri': 'partners',
}

/** "Ime (https://…)" → { name, url }; a bare name keeps url undefined. */
function parseNamedLink(raw) {
  const match = raw.trim().match(/^(.*?)\s*\((https?:\/\/[^)]+)\)$/)
  return match ? { name: match[1].trim(), url: match[2] } : { name: raw.trim() }
}

function parseProjectBody(body) {
  const paragraphs = (body || '').split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean)
  const facts = {}

  if (paragraphs.length) {
    const lines = paragraphs[0].split('\n')
    const isFactBlock = lines.every((line) =>
      Object.keys(FACT_LABELS).some((label) => line.startsWith(`${label}:`))
    )
    if (isFactBlock) {
      for (const line of lines) {
        const at = line.indexOf(':')
        const key = FACT_LABELS[line.slice(0, at)]
        const value = line.slice(at + 1).trim()
        if (key === 'partners') {
          facts.partners = value.split(/,\s*(?![^(]*\))/).map(parseNamedLink)
        } else if (key === 'leadOrganization') {
          facts.leadOrganization = parseNamedLink(value)
        } else if (key) {
          facts[key] = value
        }
      }
      paragraphs.shift()
    }
  }

  return { facts, paragraphs }
}

/** The page badges EU-funded projects differently; the flag is not stored. */
function fundingType(funding) {
  return /evropsk|european|\bEU\b|IPA/i.test(funding || '') ? 'eu' : 'national'
}

export function sectionsToProjects(sections, locale) {
  return sections.map((section, index) => {
    const { facts, paragraphs } = parseProjectBody(text(section.body, locale))
    return {
      key: `cms-${section.id ?? index}`,
      title: text(section.heading, locale),
      period: facts.period || '',
      duration: facts.duration || '',
      funding: facts.funding || '',
      fundingType: fundingType(facts.funding),
      leadOrganization: facts.leadOrganization || null,
      partners: facts.partners || [],
      paragraphs,
      docs: (section.items || []).map((item) => ({
        title: text(item.title, locale),
        file: item.href || '',
        sizeKb: item.size_kb ?? null,
        pages: item.pages ?? null,
      })),
    }
  })
}

/**
 * Library shelves. Cover images ship with the frontend rather than the CMS, so
 * they are looked up by the document's path; a document added in the admin
 * simply has no cover.
 */
export function sectionsToShelves(sections, locale, coversByFile = {}) {
  return sections.map((section) => ({
    heading: text(section.heading, locale),
    docs: (section.items || []).map((item) => {
      const file = item.href || ''
      return {
        title: text(item.title, locale),
        file,
        sizeKb: item.size_kb ?? null,
        cover: coversByFile[file] || coversByFile[file.replace(/^https?:\/\/[^/]+/, '')] || null,
        kind: /\.pdf($|\?)/i.test(file) ? 'pdf' : 'doc',
      }
    }),
  }))
}
