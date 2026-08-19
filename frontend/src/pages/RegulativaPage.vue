<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import DocumentCard from '../components/DocumentCard.vue'
import {
  bylawCategories as bundledCategories,
  primaryLegislation as bundledPrimary,
} from '../data/regulativa'
import { text, toDocument, usePageSections, withFallback } from '../cms'
import { isIOS } from '../platform'

const { t, locale } = useI18n()

// Editable under Stranice → Regulativa. The first section holds the primary
// legislation shown as cards; every later section becomes one collapsible
// category of bylaws. The bundled lists stand in until the API answers.
const sections = usePageSections('regulativa')

const primaryLegislation = withFallback(sections, bundledPrimary, (cmsSections) =>
  cmsSections[0].items.map((item) => toDocument(item, locale.value))
)

const bylawCategories = withFallback(sections, bundledCategories, (cmsSections) =>
  cmsSections.slice(1).map((section) => ({
    id: `section-${section.id}`,
    title: text(section.heading, locale.value),
    items: section.items.map((item) => toDocument(item, locale.value)),
  }))
)

const heroBadges = computed(() => [
  {
    title: t('regulations.badge1Title'),
    text: t('regulations.badge1Text'),
    icon: 'scale',
  },
  {
    title: t('regulations.badge2Title'),
    text: t('regulations.badge2Text'),
    icon: 'stack',
  },
  {
    title: t('regulations.badge3Title'),
    text: t('regulations.badge3Text'),
    icon: 'shield',
  },
])

const searchText = ref('')
const previewDoc = ref(null)

// Categories start open, so this only records the ones the visitor collapsed.
// Keyed by id and defaulting to open matters now that the ids come from the
// database: a category added in the admin must appear open like the rest, not
// silently collapsed because nothing seeded an entry for it.
const openCategories = reactive({})

function isCategoryOpen(id) {
  return openCategories[id] !== false
}

function toggleCategory(id) {
  openCategories[id] = !isCategoryOpen(id)
}

const filteredCategories = computed(() => {
  const q = searchText.value.trim().toLowerCase()
  if (!q) return bylawCategories.value
  return bylawCategories.value
    .map((category) => ({
      ...category,
      items: category.items.filter(
        (item) => item.title.toLowerCase().includes(q) || item.reference.toLowerCase().includes(q)
      ),
    }))
    .filter((category) => category.items.length)
})

const totalCount = computed(() =>
  filteredCategories.value.reduce((sum, category) => sum + category.items.length, 0)
)

function formatSize(sizeKb) {
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}

function openPreview(item) {
  if (isIOS()) {
    window.open(item.file, '_blank', 'noopener')
    return
  }
  previewDoc.value = item
}

function closePreview() {
  previewDoc.value = null
}
</script>

<template>
  <div>
  <section class="section regulativa-hero">
    <div class="container">
      <div class="regulativa-hero__text">
        <span class="regulativa-hero__label">{{ t('regulations.label') }}</span>
        <h1>{{ t('regulations.title') }}</h1>
        <p class="regulativa-hero__lead">
          {{ t('regulations.lead') }}
        </p>
      </div>

      <div class="regulativa-hero__badges">
        <div v-for="badge in heroBadges" :key="badge.title" class="hero-badge">
          <span class="hero-badge__icon" aria-hidden="true">
            <svg v-if="badge.icon === 'scale'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M12 3v18M7 21h10" stroke-linecap="round" />
              <path d="M12 5 5 8l3.5 7a4 4 0 0 0 7 0L19 8Z" stroke-linejoin="round" />
              <path d="M5 8h6M13 8h6" stroke-linecap="round" />
            </svg>
            <svg v-else-if="badge.icon === 'stack'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M12 3 3 8l9 5 9-5Z" stroke-linejoin="round" />
              <path d="M3 12l9 5 9-5" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M3 16l9 5 9-5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M12 3 4 6v6c0 5 3.5 8.5 8 9 4.5-.5 8-4 8-9V6Z" stroke-linejoin="round" />
              <path d="M8.5 12.2 11 14.7l4.8-5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <div class="hero-badge__body">
            <h3>{{ badge.title }}</h3>
            <p>{{ badge.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section--alt regulativa-primary">
    <div class="container">
      <h2 class="section-title">{{ t('regulations.primaryTitle') }}</h2>
      <div class="regulativa-primary__grid">
        <DocumentCard
          v-for="item in primaryLegislation"
          :key="item.file"
          :title="item.title"
          :file="item.file"
          :reference="item.reference"
          :pages="item.pages"
          :size-kb="item.sizeKb"
          @preview="openPreview(item)"
        />
      </div>
    </div>
  </section>

  <section class="section regulativa-bylaws">
    <div class="container">
      <div class="regulativa-bylaws__header">
        <h2>{{ t('regulations.bylawsTitle') }}</h2>
        <div class="regulativa-bylaws__search">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2" stroke-linecap="round"/></svg>
          <input v-model="searchText" type="search" :placeholder="t('regulations.searchPlaceholder')" :aria-label="t('regulations.searchAriaLabel')" />
        </div>
      </div>

      <p class="regulativa-bylaws__count">
        {{ totalCount }} {{ totalCount === 1 ? t('regulations.countSingular') : t('regulations.countPlural') }}
      </p>

      <div v-if="filteredCategories.length" class="category-list">
        <div v-for="category in filteredCategories" :key="category.id" class="category">
          <button type="button" class="category__header" @click="toggleCategory(category.id)">
            <span class="category__title">{{ category.title }}</span>
            <span class="category__count">{{ category.items.length }}</span>
            <svg
              class="category__chevron"
              :class="{ 'category__chevron--open': isCategoryOpen(category.id) || searchText }"
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

          <div v-show="isCategoryOpen(category.id) || searchText" class="bylaw-list">
            <div v-for="item in category.items" :key="item.file" class="bylaw-row">
              <span class="bylaw-row__body">
                <span class="bylaw-row__title-row">
                  <span class="bylaw-row__title">{{ item.title }}</span>
                </span>
                <span class="bylaw-row__reference">{{ item.reference }}</span>
                <span class="bylaw-row__meta">{{ item.pages }} {{ t('regulations.pageSuffix') }} · {{ formatSize(item.sizeKb) }}</span>
              </span>
              <span class="bylaw-row__actions">
                <button type="button" class="icon-btn" :title="t('regulations.previewDoc')" @click="openPreview(item)">
                  <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" stroke-linecap="round" stroke-linejoin="round" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
                <a class="icon-btn" :title="t('regulations.downloadDoc')" :href="item.file" target="_blank" rel="noopener" download>
                  <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M12 3v12m0 0-4-4m4 4 4-4M4 20h16" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </a>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="regulativa-bylaws__empty">
        <span class="regulativa-bylaws__empty-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="10.5" cy="10.5" r="6.5" />
            <line x1="15.2" y1="15.2" x2="21" y2="21" stroke-linecap="round" />
          </svg>
        </span>
        <p>{{ t('regulations.noResults') }}</p>
      </div>
    </div>
  </section>

  <div v-if="previewDoc" class="preview-overlay" @click.self="closePreview">
    <div class="preview-modal">
      <div class="preview-modal__header">
        <div class="preview-modal__title-col">
          <h3>{{ previewDoc.title }}</h3>
          <p>{{ previewDoc.reference }}</p>
        </div>
        <div class="preview-modal__actions">
          <a class="btn btn--primary" :href="previewDoc.file" target="_blank" rel="noopener" download>{{ t('regulations.download') }}</a>
          <button type="button" class="icon-btn preview-modal__close" :title="t('regulations.close')" @click="closePreview">
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
.regulativa-hero {
  padding-bottom: var(--space-5);
}

.regulativa-hero__text {
  text-align: center;
  max-width: 680px;
  margin: 0 auto;
}

.regulativa-hero__label {
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

.regulativa-hero__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  margin-top: var(--space-3);
}

.regulativa-hero__badges {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  max-width: 900px;
  margin: var(--space-6) auto 0;
}

.hero-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
  text-align: left;
}

.hero-badge__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-light);
  color: var(--color-primary);
  flex-shrink: 0;
}

.hero-badge__icon svg {
  width: 24px;
  height: 24px;
}

.hero-badge__body h3 {
  font-size: 1rem;
  margin-bottom: 2px;
}

.hero-badge__body p {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.regulativa-primary__grid {
  display: grid;
  gap: var(--space-4);
}

.regulativa-bylaws__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.regulativa-bylaws__header h2 {
  margin: 0;
}

.regulativa-bylaws__search {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 240px;
  max-width: 340px;
  padding: 9px 14px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  transition: border-color 0.15s ease;
}

.regulativa-bylaws__search:focus-within {
  border-color: var(--color-primary);
}

.regulativa-bylaws__search input {
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--color-ink);
  width: 100%;
}

.regulativa-bylaws__count {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-bottom: var(--space-4);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.category {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  overflow: hidden;
}

.category__header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-alt);
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}

.category__title {
  flex: 1;
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-ink);
}

.category__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.75rem;
  font-weight: 700;
}

.category__chevron {
  color: var(--color-text-muted);
  transition: transform 0.15s ease;
}

.category__chevron--open {
  transform: rotate(180deg);
}

.bylaw-list {
  display: flex;
  flex-direction: column;
  padding: var(--space-2);
  gap: 6px;
}

.bylaw-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-sm);
  transition: background 0.15s ease;
}

.bylaw-row:hover {
  background: var(--color-primary-light);
}

.bylaw-row__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bylaw-row__title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.bylaw-row__title {
  font-weight: 600;
  font-size: 0.95rem;
  line-height: 1.35;
}

.bylaw-row__reference {
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.bylaw-row__meta {
  color: var(--color-text-muted);
  font-size: 0.78rem;
}

.bylaw-row__actions {
  flex-shrink: 0;
  display: flex;
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

.regulativa-bylaws__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-6) 0;
}

.regulativa-bylaws__empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: var(--space-3);
}

.regulativa-bylaws__empty-icon svg {
  width: 30px;
  height: 30px;
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

@media (max-width: 900px) {
  .regulativa-hero__badges {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .regulativa-bylaws__header {
    flex-direction: column;
    align-items: stretch;
  }

  .regulativa-bylaws__search {
    max-width: none;
  }

  .preview-modal {
    height: 92vh;
  }

  .bylaw-row {
    flex-wrap: wrap;
  }

  .bylaw-row__actions {
    width: 100%;
    justify-content: flex-end;
  }

  .preview-modal__header {
    flex-direction: column;
    align-items: stretch;
  }

  .preview-modal__actions {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .regulativa-hero__lead {
    font-size: 0.95rem;
  }

  .hero-badge {
    padding: var(--space-3);
  }

  .regulativa-hero__badges {
    margin-top: var(--space-4);
  }

  .category__header {
    padding: var(--space-3);
  }
}
</style>
