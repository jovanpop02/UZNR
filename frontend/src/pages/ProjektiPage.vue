<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { projects as bundledProjects } from '../data/projekti'
import { sectionsToProjects, usePageSections, withFallback } from '../cms'
import ppeIconsBanner from '../assets/projekti/ppe-icons-banner.jpg'
import euFlag from '../assets/projekti/eu-flag.png'
import mneCoatOfArms from '../assets/projekti/mne-coat-of-arms.jpg'
import { isIOS } from '../platform'

const { t, locale } = useI18n()

// Editable under Projekti in the admin; the bundled list renders immediately
// and stands in if the backend is asleep or unreachable.
const sections = usePageSections('projekti')
const projects = withFallback(sections, bundledProjects, (cmsSections) =>
  sectionsToProjects(cmsSections, locale.value)
)

const fundingBadge = computed(() => ({
  eu: { icon: euFlag, label: t('projects.fundingEu') },
  national: { icon: mneCoatOfArms, label: t('projects.fundingNational') },
}))

// Keyed by project, but filled in on demand rather than up front: the list now
// arrives from the API, so the keys are not known when this runs.
const openDocs = reactive({})
const searchText = reactive({})

function docsOpen(project) {
  if (project.key in openDocs) return openDocs[project.key]
  // A short list is more useful open than folded away.
  return project.docs.length > 0 && project.docs.length <= 3
}

function toggleDocs(key) {
  const project = projects.value.find((p) => p.key === key)
  openDocs[key] = !(project ? docsOpen(project) : false)
}

function filteredDocs(project) {
  const q = (searchText[project.key] || '').trim().toLowerCase()
  if (!q) return project.docs
  return project.docs.filter((d) => d.title.toLowerCase().includes(q))
}

function formatSize(sizeKb) {
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}

const previewDoc = ref(null)

function openPreview(doc) {
  if (isIOS()) {
    window.open(doc.file, '_blank', 'noopener')
    return
  }
  previewDoc.value = doc
}

function closePreview() {
  previewDoc.value = null
}

const totalDocs = computed(() =>
  projects.value.reduce((sum, p) => sum + p.docs.length, 0)
)
const totalProjects = computed(() => projects.value.length)
</script>

<template>
  <div>
  <section class="section projekti-hero">
    <div class="container projekti-hero__inner">
      <span class="projekti-hero__label">{{ t('projects.label') }}</span>
      <h1>{{ t('projects.title') }}</h1>
      <p class="projekti-hero__lead">
        {{ t('projects.lead') }}
      </p>
      <div class="projekti-hero__stats">
        <div class="projekti-stat">
          <span class="projekti-stat__value">{{ totalProjects }}</span>
          <span class="projekti-stat__label">{{ t('projects.statProjects') }}</span>
        </div>
        <div class="projekti-stat">
          <span class="projekti-stat__value">{{ totalDocs }}</span>
          <span class="projekti-stat__label">{{ t('projects.statDocs') }}</span>
        </div>
      </div>
      <img :src="ppeIconsBanner" :alt="t('projects.bannerAlt')" class="projekti-hero__banner" />
    </div>
  </section>

  <section
    v-for="(project, index) in projects"
    :key="project.key"
    class="section projekti-project"
    :class="{ 'section--alt': index % 2 === 1 }"
  >
    <div class="container">
      <div class="project-card">
        <div class="project-card__header">
          <div class="project-card__badge" v-if="fundingBadge[project.fundingType]">
            <img :src="fundingBadge[project.fundingType].icon" alt="" class="project-card__badge-icon" />
            <span>{{ fundingBadge[project.fundingType].label }}</span>
          </div>
          <h2>{{ project.title }}</h2>
          <div class="project-card__meta">
            <span v-if="project.period" class="meta-chip">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
              {{ project.period }}
            </span>
            <span v-if="project.duration" class="meta-chip">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9" /><polyline points="12 7 12 12 15.5 14" /></svg>
              {{ project.duration }}
            </span>
            <span v-if="project.funding" class="meta-chip meta-chip--funding">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M9.5 15a2.5 2.5 0 0 0 2.5 1.5c1.5 0 2.5-.8 2.5-2s-1-1.7-2.5-2-2.5-.8-2.5-2 1-2 2.5-2a2.5 2.5 0 0 1 2.5 1.5" stroke-linecap="round" /><line x1="12" y1="6" x2="12" y2="18" /></svg>
              {{ project.funding }}
            </span>
          </div>
          <p v-if="project.leadOrganization" class="project-card__lead-org">
            <strong>{{ t('projects.leadOrganization') }}</strong>{{ ' ' }}
            <a v-if="project.leadOrganization.url" :href="project.leadOrganization.url" target="_blank" rel="noopener">{{ project.leadOrganization.name }}</a>
            <span v-else>{{ project.leadOrganization.name }}</span>
          </p>
        </div>

        <div class="project-card__body">
          <p v-for="(p, i) in project.paragraphs" :key="i">{{ p }}</p>
        </div>

        <div v-if="(project.partners && project.partners.length) || project.leadOrganization" class="project-card__partners">
          <h3 class="project-card__partners-title">{{ t('projects.partnersTitle') }}</h3>
          <div class="partner-chips">
            <template v-if="project.leadOrganization">
              <a
                v-if="project.leadOrganization.url"
                class="partner-chip partner-chip--lead partner-chip--link"
                :href="project.leadOrganization.url"
                target="_blank"
                rel="noopener"
              >
                <span class="partner-chip__tag">{{ t('projects.leadTag') }}</span>{{ project.leadOrganization.name }}
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" stroke-linecap="round" stroke-linejoin="round" /></svg>
              </a>
              <span v-else class="partner-chip partner-chip--lead">
                <span class="partner-chip__tag">{{ t('projects.leadTag') }}</span>{{ project.leadOrganization.name }}
              </span>
            </template>
            <template v-for="partner in project.partners" :key="partner.name">
              <a v-if="partner.url" class="partner-chip partner-chip--link" :href="partner.url" target="_blank" rel="noopener">
                {{ partner.name }}
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" stroke-linecap="round" stroke-linejoin="round" /></svg>
              </a>
              <span v-else class="partner-chip">{{ partner.name }}</span>
            </template>
          </div>
        </div>

        <div v-if="project.associates && project.associates.length" class="project-card__partners">
          <h3 class="project-card__partners-title">{{ t('projects.associatesTitle') }}</h3>
          <div class="partner-chips">
            <template v-for="associate in project.associates" :key="associate.name">
              <a v-if="associate.url" class="partner-chip partner-chip--link" :href="associate.url" target="_blank" rel="noopener">
                {{ associate.name }}
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8" stroke-linecap="round" stroke-linejoin="round" /></svg>
              </a>
              <span v-else class="partner-chip">{{ associate.name }}</span>
            </template>
          </div>
        </div>

        <div v-if="project.docs.length" class="project-card__docs">
          <button type="button" class="docs-toggle" @click="toggleDocs(project.key)">
            <span class="docs-toggle__title">
              {{ project.docsIntro || t('projects.docsDefault') }}
              <span class="docs-toggle__count">{{ project.docs.length }}</span>
            </span>
            <svg
              class="docs-toggle__chevron"
              :class="{ 'docs-toggle__chevron--open': docsOpen(project) }"
              viewBox="0 0 24 24"
              width="18"
              height="18"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>

          <div v-show="docsOpen(project)" class="docs-panel">
            <div v-if="project.docs.length > 8" class="docs-search">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7" /><line x1="21" y1="21" x2="16.2" y2="16.2" stroke-linecap="round" /></svg>
              <input v-model="searchText[project.key]" type="search" :placeholder="t('projects.searchDocsPlaceholder')" :aria-label="t('projects.searchDocsAriaLabel', { title: project.title })" />
            </div>

            <ul class="docs-list">
              <li v-for="doc in filteredDocs(project)" :key="doc.file" class="docs-list__item">
                <span class="docs-list__icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 3h9l3 3v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M15 3v3a1 1 0 0 0 1 1h3" /></svg>
                </span>
                <span class="docs-list__body">
                  <span class="docs-list__title">{{ doc.title }}</span>
                  <span v-if="doc.pages || doc.sizeKb" class="docs-list__meta">
                    <template v-if="doc.pages">{{ doc.pages }} {{ doc.pages === 1 ? t('projects.pageSingular') : t('projects.pagePlural') }} · </template>{{ formatSize(doc.sizeKb) }}
                  </span>
                </span>
                <span class="docs-list__actions">
                  <button type="button" class="icon-btn" :title="t('projects.previewDoc')" @click="openPreview(doc)">
                    <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" stroke-linecap="round" stroke-linejoin="round" /><circle cx="12" cy="12" r="3" /></svg>
                  </button>
                  <a class="icon-btn" :title="t('projects.downloadDoc')" :href="doc.file" target="_blank" rel="noopener" download>
                    <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3v12m0 0-4-4m4 4 4-4M4 20h16" stroke-linecap="round" stroke-linejoin="round" /></svg>
                  </a>
                </span>
              </li>
              <li v-if="!filteredDocs(project).length" class="docs-list__empty">{{ t('projects.noDocsMatch') }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>

  <div v-if="previewDoc" class="preview-overlay" @click.self="closePreview">
    <div class="preview-modal">
      <div class="preview-modal__header">
        <div class="preview-modal__title-col">
          <h3>{{ previewDoc.title }}</h3>
          <p v-if="previewDoc.pages || previewDoc.sizeKb">
            <template v-if="previewDoc.pages">{{ previewDoc.pages }} {{ previewDoc.pages === 1 ? t('projects.pageSingular') : t('projects.pagePlural') }} · </template>{{ formatSize(previewDoc.sizeKb) }}
          </p>
        </div>
        <div class="preview-modal__actions">
          <a class="btn btn--primary" :href="previewDoc.file" target="_blank" rel="noopener" download>{{ t('projects.download') }}</a>
          <button type="button" class="icon-btn preview-modal__close" :title="t('projects.close')" @click="closePreview">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" /></svg>
          </button>
        </div>
      </div>
      <embed :src="previewDoc.file" type="application/pdf" class="preview-modal__frame" />
    </div>
  </div>
  </div>
</template>

<style scoped>
.projekti-hero {
  padding-bottom: var(--space-5);
}

.projekti-hero__inner {
  max-width: 780px;
  margin: 0 auto;
  text-align: center;
}

.projekti-hero__label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: var(--space-3);
}

.projekti-hero__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  margin-top: var(--space-3);
}

.projekti-hero__stats {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  margin-top: var(--space-5);
}

.projekti-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.projekti-stat__value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-primary);
  line-height: 1.1;
}

.projekti-stat__label {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-top: 2px;
}

.projekti-hero__banner {
  width: 100%;
  max-width: 640px;
  margin: var(--space-6) auto 0;
  border-radius: var(--radius-md);
  display: block;
}

.projekti-project {
  scroll-margin-top: 90px;
}

.project-card {
  max-width: 880px;
  margin: 0 auto;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.project-card__badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 6px;
  border-radius: 999px;
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

.project-card__badge-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.project-card__header h2 {
  margin-bottom: var(--space-3);
}

.project-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: var(--space-3);
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.8rem;
  font-weight: 600;
}

.meta-chip--funding {
  background: var(--color-bg-alt);
  color: var(--color-text);
}

.project-card__lead-org {
  color: var(--color-text-muted);
  font-size: 0.92rem;
  margin-bottom: var(--space-4);
}

.project-card__lead-org a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.project-card__lead-org a:hover {
  text-decoration: underline;
}

.project-card__body p {
  color: var(--color-text);
}

.project-card__body p + p {
  margin-top: var(--space-3);
}

.project-card__partners {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-border);
}

.project-card__partners-title {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

.partner-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.partner-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border);
  font-size: 0.83rem;
  color: var(--color-text);
  text-decoration: none;
}

.partner-chip--link {
  color: var(--color-primary-dark);
  font-weight: 600;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.partner-chip--link:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.partner-chip--link svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.partner-chip--lead {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.partner-chip__tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 7px;
  margin-right: 2px;
  border-radius: 999px;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.project-card__docs {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-border);
}

.docs-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  padding: 0;
  text-align: left;
}

.docs-toggle__title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-ink);
}

.docs-toggle__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.75rem;
  font-weight: 700;
}

.docs-toggle__chevron {
  color: var(--color-text-muted);
  transition: transform 0.15s ease;
  flex-shrink: 0;
}

.docs-toggle__chevron--open {
  transform: rotate(180deg);
}

.docs-panel {
  margin-top: var(--space-4);
}

.docs-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
  max-width: 340px;
  transition: border-color 0.15s ease;
}

.docs-search:focus-within {
  border-color: var(--color-primary);
}

.docs-search input {
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--color-ink);
  width: 100%;
}

.docs-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.docs-list__item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px var(--space-3);
  border-radius: var(--radius-sm);
  transition: background 0.15s ease;
}

.docs-list__item:hover {
  background: var(--color-primary-light);
}

.docs-list__icon {
  flex-shrink: 0;
  display: inline-flex;
  color: var(--color-primary);
}

.docs-list__icon svg {
  width: 18px;
  height: 18px;
}

.docs-list__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.docs-list__title {
  font-size: 0.88rem;
  line-height: 1.35;
  color: var(--color-text);
}

.docs-list__meta {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.docs-list__actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

.docs-list__empty {
  color: var(--color-text-muted);
  font-size: 0.88rem;
  padding: var(--space-3);
  text-align: center;
}

.icon-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
  padding: 0;
}

.icon-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

@media (max-width: 560px) {
  .project-card {
    padding: var(--space-4);
  }

  .projekti-hero__stats {
    gap: var(--space-5);
  }

  .docs-list__item {
    flex-wrap: wrap;
  }

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

.preview-modal__frame {
  flex: 1;
  width: 100%;
  border: none;
}
</style>
