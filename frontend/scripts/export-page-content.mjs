/**
 * Exports the page content that currently lives in `src/data/*.js` into JSON the
 * backend can seed its CMS from.
 *
 * Run once when moving a page's content into the admin:
 *
 *   node scripts/export-page-content.mjs ../proba/content/seed_data/pages
 *
 * After that the database is the source of truth and this script is only useful
 * for re-seeding an empty install — it does not read the database back, so it
 * will not pick up edits made in the admin.
 */

import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const outDir = resolve(here, process.argv[2] ?? '../../proba/content/seed_data/pages')

const { primaryLegislation, bylawCategories } = await import('../src/data/regulativa.js')
const { publications } = await import('../src/data/publikacije.js')
const { pressClippings } = await import('../src/data/press.js')
const { faqs } = await import('../src/data/pitanja.js')

const doc = (item, order) => ({
  title: item.title,
  reference: item.reference ?? '',
  url: '',
  file: item.file ?? '',
  pages: item.pages ?? null,
  size_kb: item.sizeKb ?? null,
  date_label: item.dateLabel ?? '',
  order,
})

const pages = [
  {
    slug: 'regulativa',
    title: 'Regulativa',
    title_en: 'Regulations',
    sections: [
      {
        kind: 'documents',
        heading: 'Osnovni propisi',
        heading_en: 'Primary legislation',
        order: 0,
        items: primaryLegislation.map(doc),
      },
      ...bylawCategories.map((category, index) => ({
        kind: 'documents',
        heading: category.title,
        heading_en: '',
        order: index + 1,
        items: category.items.map(doc),
      })),
    ],
  },
  {
    slug: 'publikacije',
    title: 'Publikacije',
    title_en: 'Publications',
    sections: [
      {
        kind: 'documents',
        heading: 'Publikacije',
        heading_en: 'Publications',
        order: 0,
        items: publications.map(doc),
      },
    ],
  },
  {
    slug: 'press',
    title: 'Press / Mediji',
    title_en: 'Press / Media',
    sections: [
      {
        kind: 'links',
        heading: 'Medijske objave',
        heading_en: 'Media coverage',
        order: 0,
        items: pressClippings.map((clip, order) => ({
          title: clip.title,
          reference: clip.source ?? '',
          date_label: clip.date ?? '',
          url: clip.href ?? '',
          file: '',
          image: clip.thumb ?? '',
          order,
        })),
      },
    ],
  },
  {
    slug: 'pitanja-odgovori',
    title: 'Pitanja i odgovori',
    title_en: 'Questions and answers',
    sections: [
      {
        kind: 'faq',
        heading: 'Najčešća pitanja',
        heading_en: 'Frequently asked questions',
        order: 0,
        items: faqs.map((faq, order) => ({
          title: faq.question,
          // Answers are stored as blocks; flatten them into paragraphs, keeping
          // list items as dashes so the text survives the round trip readably.
          description: faq.answer
            .map((block) =>
              block.type === 'list'
                ? block.value.map((line) => `- ${line}`).join('\n')
                : block.value
            )
            .join('\n\n'),
          url: '',
          file: '',
          order,
        })),
      },
    ],
  },
]

mkdirSync(outDir, { recursive: true })
for (const page of pages) {
  const target = resolve(outDir, `${page.slug}.json`)
  writeFileSync(target, `${JSON.stringify(page, null, 2)}\n`, 'utf8')
  const items = page.sections.reduce((sum, section) => sum + section.items.length, 0)
  console.log(`${page.slug}: ${page.sections.length} sections, ${items} items -> ${target}`)
}
