<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import DocumentCard from '../components/DocumentCard.vue'
import { sectionsToShelves, usePageSections, withFallback } from '../cms'
import euOshaLogo from '../assets/biblioteka/eu-osha-logo.svg'
import ioshLogo from '../assets/biblioteka/iosh-logo.png'
import euOshaPosterCover from '../assets/biblioteka/eu-osha-poster-cover.jpg'
import euOshaFlyerCover from '../assets/biblioteka/eu-osha-flyer-cover.jpg'
import euOshaKampanjaCover from '../assets/biblioteka/eu-osha-kampanja-cover.jpg'
import euOshaFlajerMneCover from '../assets/biblioteka/eu-osha-flajer-mne-cover.jpg'
import euOshaVodicMneCover from '../assets/biblioteka/eu-osha-vodic-mne-cover.jpg'
import euOshaLeafletMneCover from '../assets/biblioteka/eu-osha-leaflet-mne-cover.jpg'
import { isIOS } from '../platform'

const { t, locale } = useI18n()

const navLinks = [
  { id: 'strucni-ispit', labelKey: 'library.navExam' },
  { id: 'eu-osha', label: 'EU OSHA' },
  { id: 'no-time-to-lose', label: 'No Time to Lose' },
]

// Cover images ship with the frontend, so a document coming from the admin is
// matched to its cover by path. One added later simply has no cover.
const COVERS_BY_FILE = {
  '/documents/biblioteka/eu-osha-poster.pdf': euOshaPosterCover,
  '/documents/biblioteka/eu-osha-flyer.pdf': euOshaFlyerCover,
  '/documents/biblioteka/eu-osha-kampanja.pdf': euOshaKampanjaCover,
  '/documents/biblioteka/B3flajer-zdrava-radna-mjesta.pdf': euOshaFlajerMneCover,
  '/documents/biblioteka/B5vodic-zdrava-radna-mjesta.pdf': euOshaVodicMneCover,
  '/documents/biblioteka/B4leaflet-zdrava-radna-mjesta.pdf': euOshaLeafletMneCover,
}

const bundledStrucniIspitDocs = [
  {
    title: 'Pravilnik o polaganju stručnog ispita za lica koja se bave poslovima zaštite na radu',
    file: '/documents/biblioteka/strucni-ispit-pravilnik.pdf',
    sizeKb: 63,
    kind: 'pdf',
  },
  {
    title: 'Prijava za polaganje stručnog ispita',
    file: '/documents/biblioteka/strucni-ispit-prijava.doc',
    sizeKb: 37,
    kind: 'doc',
  },
]

const formatRows = computed(() =>
  Array.from({ length: 13 }, (_, i) => ({
    label: t(`library.formatLabel${i + 1}`),
    value: t(`library.formatValue${i + 1}`),
  }))
)

const troskovi = computed(() => Array.from({ length: 5 }, (_, i) => t(`library.troskovi${i + 1}`)))

const bundledEuOshaMainDocs = [
  { title: 'Poster kampanje', file: '/documents/biblioteka/eu-osha-poster.pdf', sizeKb: 984, cover: euOshaPosterCover, kind: 'pdf' },
  { title: 'Flajer kampanje', file: '/documents/biblioteka/eu-osha-flyer.pdf', sizeKb: 437, cover: euOshaFlyerCover, kind: 'pdf' },
  { title: 'Vodič kroz kampanju', file: '/documents/biblioteka/eu-osha-kampanja.pdf', sizeKb: 617, cover: euOshaKampanjaCover, kind: 'pdf' },
]

const bundledEuOshaStressDocs = [
  { title: 'Flajer — Upravljanje stresom', file: '/documents/biblioteka/B3flajer-zdrava-radna-mjesta.pdf', sizeKb: 2573, cover: euOshaFlajerMneCover, kind: 'pdf' },
  { title: 'Vodič — Upravljanje stresom', file: '/documents/biblioteka/B5vodic-zdrava-radna-mjesta.pdf', sizeKb: 53380, cover: euOshaVodicMneCover, kind: 'pdf' },
  { title: 'Letak — Upravljanje stresom', file: '/documents/biblioteka/B4leaflet-zdrava-radna-mjesta.pdf', sizeKb: 962, cover: euOshaLeafletMneCover, kind: 'pdf' },
]

// Editable under Biblioteka in the admin. The three shelves are matched by
// position, which is the order they are listed in there.
const sections = usePageSections('biblioteka')
const shelves = withFallback(
  sections,
  [
    { heading: '', docs: bundledStrucniIspitDocs },
    { heading: '', docs: bundledEuOshaMainDocs },
    { heading: '', docs: bundledEuOshaStressDocs },
  ],
  (cmsSections) => sectionsToShelves(cmsSections, locale.value, COVERS_BY_FILE)
)

const strucniIspitDocs = computed(() => shelves.value[0]?.docs ?? [])
const euOshaMainDocs = computed(() => shelves.value[1]?.docs ?? [])
const euOshaStressDocs = computed(() => shelves.value[2]?.docs ?? [])

const previewDoc = ref(null)
const activeSection = ref(navLinks[0].id)
let observer = null

function formatSize(sizeKb) {
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}

function openPreview(doc) {
  if (doc.kind !== 'pdf' || isIOS()) {
    window.open(doc.file, '_blank', 'noopener')
    return
  }
  previewDoc.value = doc
}

function closePreview() {
  previewDoc.value = null
}

onMounted(() => {
  const sections = navLinks.map((link) => document.getElementById(link.id)).filter(Boolean)

  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)
      if (visible[0]) {
        activeSection.value = visible[0].target.id
      }
    },
    { rootMargin: '-35% 0px -55% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] }
  )

  sections.forEach((section) => observer.observe(section))
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <div>
  <section class="section biblioteka-hero">
    <div class="container">
      <h1>{{ t('library.heroTitle') }}</h1>
      <p class="biblioteka-hero__lead">
        {{ t('library.heroLead') }}
      </p>
    </div>
  </section>

  <nav class="biblioteka-nav" :aria-label="t('library.sectionsAriaLabel')">
    <div class="biblioteka-nav__inner">
      <a
        v-for="link in navLinks"
        :key="link.id"
        :href="`#${link.id}`"
        class="biblioteka-nav__link"
        :class="{ 'biblioteka-nav__link--active': activeSection === link.id }"
      >
        {{ link.labelKey ? t(link.labelKey) : link.label }}
      </a>
    </div>
  </nav>

  <section id="strucni-ispit" class="section biblioteka-section">
    <div class="container">
      <h2 class="section-title">{{ t('library.examTitle') }}</h2>

      <p class="biblioteka-section__text">
        {{ t('library.examIntro') }}
      </p>

      <div class="doc-grid">
        <DocumentCard
          v-for="doc in strucniIspitDocs"
          :key="doc.file"
          :title="doc.title"
          :file="doc.file"
          :size-kb="doc.sizeKb"
          :kind="doc.kind"
          show-kind
          @preview="openPreview(doc)"
        />
      </div>

      <h3 class="biblioteka-subheading">{{ t('library.writtenWorkTitle') }}</h3>
      <p class="biblioteka-section__text">
        {{ t('library.writtenWorkIntro') }}
      </p>

      <div class="table-wrap">
        <table class="format-table">
          <thead>
            <tr>
              <th>{{ t('library.tableColData') }}</th>
              <th>{{ t('library.tableColDesc') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in formatRows" :key="row.label">
              <td>{{ row.label }}</td>
              <td>{{ row.value }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="info-grid">
        <div class="info-card">
          <h3>{{ t('library.examRokoviTitle') }}</h3>
          <p>{{ t('library.examRokoviText') }}</p>
        </div>
        <div class="info-card">
          <h3>{{ t('library.examMjestoTitle') }}</h3>
          <p>{{ t('library.examMjestoText') }}</p>
        </div>
        <div class="info-card info-card--alert">
          <h3>{{ t('library.examNapomenaTitle') }}</h3>
          <p>{{ t('library.examNapomenaText') }}</p>
        </div>
      </div>

      <h3 class="biblioteka-subheading">{{ t('library.costsTitle') }}</h3>
      <ul class="text-list">
        <li v-for="line in troskovi" :key="line">{{ line }}</li>
      </ul>

      <div class="contact-card">
        <span class="contact-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke-linecap="round" />
          </svg>
        </span>
        <div>
          <h3>{{ t('library.contactPersonTitle') }}</h3>
          <p>
            {{ t('library.contactPersonInfo') }} ·
            <a href="tel:+38267277389">+382 67 277 389</a> ·
            <a href="mailto:svetlana.milosevic@mrs.gov.me">svetlana.milosevic@mrs.gov.me</a>
          </p>
        </div>
      </div>
    </div>
  </section>

  <section id="eu-osha" class="section section--alt biblioteka-section">
    <div class="container">
      <div class="section-intro">
        <img class="section-intro__logo" :src="euOshaLogo" alt="EU-OSHA logo" />
        <div>
          <h2 class="section-title">EU OSHA</h2>
          <p class="biblioteka-section__text">
            {{ t('library.euOshaIntro') }}
          </p>
          <a class="btn btn--primary" href="https://osha.europa.eu/en" target="_blank" rel="noopener">
            {{ t('library.euOshaVisitBtn') }}
          </a>
        </div>
      </div>

      <h3 class="biblioteka-subheading">{{ t('library.euOshaCampaignTitle') }}</h3>
      <div class="media-grid">
        <div v-for="doc in euOshaMainDocs" :key="doc.file" class="media-card">
          <button type="button" class="media-card__image" @click="openPreview(doc)">
            <img :src="doc.cover" :alt="doc.title" loading="lazy" />
          </button>
          <div class="media-card__body">
            <h3>{{ doc.title }}</h3>
            <p class="media-card__meta">PDF · {{ formatSize(doc.sizeKb) }}</p>
            <a class="btn btn--primary media-card__cta" :href="doc.file" target="_blank" rel="noopener" download>
              {{ t('library.download') }}
            </a>
          </div>
        </div>
      </div>

      <h3 class="biblioteka-subheading">{{ t('library.euOshaStressTitle') }}</h3>
      <div class="media-grid">
        <div v-for="doc in euOshaStressDocs" :key="doc.file" class="media-card">
          <button type="button" class="media-card__image" @click="openPreview(doc)">
            <img :src="doc.cover" :alt="doc.title" loading="lazy" />
          </button>
          <div class="media-card__body">
            <h3>{{ doc.title }}</h3>
            <p class="media-card__meta">PDF · {{ formatSize(doc.sizeKb) }}</p>
            <a class="btn btn--primary media-card__cta" :href="doc.file" target="_blank" rel="noopener" download>
              {{ t('library.download') }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="no-time-to-lose" class="section biblioteka-section">
    <div class="container">
      <h2 class="section-title">No Time to Lose</h2>

      <div class="iosh-card">
        <span class="iosh-card__logo">
          <img :src="ioshLogo" alt="IOSH logo" />
        </span>
        <div class="iosh-card__body">
          <p class="campaign-card__kicker">{{ t('library.ioshKicker') }}</p>
          <p class="campaign-card__quote">„We exist to make work safer and healthier around the world.“</p>
          <p class="campaign-card__text">
            {{ t('library.ioshText') }}
          </p>
          <a class="btn btn--primary" href="https://iosh.com/" target="_blank" rel="noopener">
            {{ t('library.ioshVisitBtn') }}
          </a>
        </div>
      </div>
    </div>
  </section>

  <div v-if="previewDoc" class="preview-overlay" @click.self="closePreview">
    <div class="preview-modal">
      <div class="preview-modal__header">
        <div class="preview-modal__title-col">
          <h3>{{ previewDoc.title }}</h3>
          <p>{{ formatSize(previewDoc.sizeKb) }}</p>
        </div>
        <div class="preview-modal__actions">
          <a class="btn btn--primary" :href="previewDoc.file" target="_blank" rel="noopener" download>{{ t('library.download') }}</a>
          <button type="button" class="icon-btn preview-modal__close" :title="t('library.close')" @click="closePreview">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
            </svg>
          </button>
        </div>
      </div>
      <embed :src="previewDoc.file" type="application/pdf" class="preview-modal__frame" />
    </div>
  </div>
  </div>
</template>

<style scoped>
#strucni-ispit,
#eu-osha,
#no-time-to-lose {
  scroll-margin-top: 140px;
}

.biblioteka-hero {
  padding-bottom: var(--space-5);
}

.biblioteka-hero__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  max-width: 640px;
  margin-top: var(--space-3);
}

.biblioteka-nav {
  position: sticky;
  top: 76px;
  z-index: 30;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

.biblioteka-nav__inner {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: var(--space-2);
  max-width: var(--container-width);
  margin-inline: auto;
  padding: var(--space-3) var(--space-4);
}

.biblioteka-nav__link {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  padding: 8px 18px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  color: var(--color-ink);
  font-weight: 600;
  font-size: 0.88rem;
  text-decoration: none;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.biblioteka-nav__link:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.biblioteka-nav__link--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.biblioteka-section__text {
  color: var(--color-text-muted);
  max-width: 760px;
  margin-bottom: var(--space-5);
}

.biblioteka-subheading {
  margin-top: var(--space-6);
  margin-bottom: var(--space-3);
}

.doc-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

/* Grid items default to min-width:auto, so a wide child (a long document title
   or the action button) stops the 1fr column shrinking and pushes the whole
   grid past the viewport — visible as horizontal page scroll around 768px. */
.doc-grid > *,
.info-grid > *,
.media-grid > * {
  min-width: 0;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-6);
}

.format-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.format-table th,
.format-table td {
  text-align: left;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
}

.format-table th {
  background: var(--color-bg-alt);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.format-table td:first-child {
  font-weight: 600;
  color: var(--color-ink);
  white-space: nowrap;
}

.format-table tr:last-child td {
  border-bottom: none;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.info-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.info-card h3 {
  font-size: 0.95rem;
  margin-bottom: 6px;
}

.info-card p {
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

.info-card--alert {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.info-card--alert h3 {
  color: var(--color-primary-dark);
}

.info-card--alert p {
  color: var(--color-primary-dark);
  font-weight: 600;
}

.text-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  color: var(--color-text-muted);
  font-size: 0.92rem;
  margin: 0 0 var(--space-6);
  padding-left: 1.2em;
}

.contact-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}

.contact-card__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.contact-card__icon svg {
  width: 24px;
  height: 24px;
}

.contact-card h3 {
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.contact-card p {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.contact-card a {
  color: var(--color-primary-dark);
  font-weight: 600;
  text-decoration: none;
}

.contact-card a:hover {
  text-decoration: underline;
}

.section-intro {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.section-intro__logo {
  flex-shrink: 0;
  width: 88px;
  height: 88px;
  object-fit: contain;
  border-radius: 50%;
  background: #fff;
  border: 1px solid var(--color-border);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.section-intro .section-title {
  margin-bottom: var(--space-2);
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.media-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.media-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.media-card__image {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: var(--color-bg-alt);
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
}

.media-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.2s ease;
}

.media-card:hover .media-card__image img {
  transform: scale(1.03);
}

.media-card__body {
  padding: var(--space-4);
}

.media-card__body h3 {
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.media-card__meta {
  color: var(--color-text-muted);
  font-size: 0.8rem;
  margin-bottom: var(--space-3);
}

.media-card__cta {
  width: 100%;
  justify-content: center;
}

.campaign-card__kicker {
  color: var(--color-primary);
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.campaign-card__quote {
  font-size: 1.3rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--color-ink);
  margin: 0 0 var(--space-3);
  padding-left: 18px;
  border-left: 3px solid var(--color-primary);
}

.campaign-card__text {
  color: var(--color-text-muted);
  max-width: 560px;
  margin-bottom: var(--space-4);
}

.iosh-card {
  display: flex;
  gap: var(--space-5);
  align-items: flex-start;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.iosh-card__logo {
  flex-shrink: 0;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: #fff;
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.iosh-card__logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.iosh-card__body {
  min-width: 0;
}

.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(23, 33, 28, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  z-index: 100;
}

.preview-modal {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
}

.preview-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.preview-modal__title-col h3 {
  font-size: 1rem;
  margin-bottom: 2px;
}

.preview-modal__title-col p {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.preview-modal__actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
}

.icon-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.preview-modal__frame {
  flex: 1;
  width: 100%;
  border: none;
}

@media (max-width: 900px) {
  .media-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 700px) {
  .doc-grid,
  .info-grid,
  .media-grid {
    grid-template-columns: 1fr;
  }

  .contact-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .section-intro {
    flex-direction: column;
    align-items: flex-start;
  }

  .iosh-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 560px) {
  .format-table thead {
    display: none;
  }

  .format-table,
  .format-table tbody,
  .format-table tr,
  .format-table td {
    display: block;
    width: 100%;
  }

  .format-table tr {
    padding: 10px 16px;
  }

  .format-table tr:not(:last-child) {
    border-bottom: 1px solid var(--color-border);
  }

  .format-table td {
    padding: 3px 0;
    border-bottom: none;
  }

  .format-table td:first-child {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-primary-dark);
  }
}

@media (max-width: 480px) {
  .preview-modal {
    height: 92vh;
  }

  .preview-modal__header {
    flex-direction: column;
    align-items: stretch;
  }

  .preview-modal__actions {
    justify-content: space-between;
  }
}
</style>
