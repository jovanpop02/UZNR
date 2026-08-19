<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { publications as bundledPublications } from '../data/publikacije'
import { toDocument, usePageSections, withFallback } from '../cms'
import { isIOS } from '../platform'
import documentsIllustration from '../assets/illustrations/documents.svg'

const { t, locale } = useI18n()
const previewDoc = ref(null)

// Editable under Stranice → Publikacije in the admin; the bundled list is the
// fallback while the backend wakes up or if it is unreachable.
const sections = usePageSections('publikacije')
const publications = withFallback(sections, bundledPublications, (cmsSections) =>
  cmsSections.flatMap((section) => section.items.map((item) => toDocument(item, locale.value)))
)

function formatSize(sizeKb) {
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}

// The publications are all PDFs, so an identical file icon on every row told a
// reader nothing. Each title already announces what the document is ("Vodic
// za...", "Studija...", "Prirucnik..."), so the kind is taken from the title's
// own opening words: it needs no new CMS field, and it stays in whichever
// language the title is written in. Anything unrecognised falls back to a
// neutral document tone rather than being mislabelled.
const KINDS = [
  { tone: 'guide', icon: 'guide', match: /^(vodič|guide)/i },
  { tone: 'study', icon: 'study', match: /^(studija|study)/i },
  { tone: 'manual', icon: 'manual', match: /^(priručnik|manual|handbook)/i },
  { tone: 'report', icon: 'report', match: /^(izvještaj|report)/i },
  { tone: 'profile', icon: 'profile', match: /^(nacionalni profil|national profile)/i },
]

function kindOf(title) {
  const clean = (title ?? '').trim()
  const hit = KINDS.find((k) => k.match.test(clean))
  if (!hit) return { tone: 'doc', icon: 'doc', label: null }
  // Label the chip with the exact words that matched, so multi-word kinds stay
  // whole ("Nacionalni profil", not "Nacionalni") and the chip reads in the
  // same language as the title itself.
  const label = clean.match(hit.match)[0]
  return { ...hit, label }
}

function openPreview(pub) {
  if (isIOS()) {
    window.open(pub.file, '_blank', 'noopener')
    return
  }
  previewDoc.value = pub
}

function closePreview() {
  previewDoc.value = null
}
</script>

<template>
  <div>
  <section class="section publikacije-hero">
    <div class="container publikacije-hero__inner">
      <div class="publikacije-hero__text">
        <h1>{{ t('publications.title') }}</h1>
        <p class="publikacije-hero__lead">
          {{ t('publications.lead') }}
        </p>
      </div>
      <img
        class="publikacije-hero__illustration"
        :src="documentsIllustration"
        alt=""
        aria-hidden="true"
        loading="lazy"
      />
    </div>
  </section>

  <section class="section section--alt publikacije-list">
    <div class="container">
      <div class="publikacije-grid">
        <div
          v-for="pub in publications"
          :key="pub.title"
          class="publication-card"
          :class="`publication-card--${kindOf(pub.title).tone}`"
        >
          <span class="publication-card__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <template v-if="kindOf(pub.title).icon === 'guide'">
                <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v15H6.5A2.5 2.5 0 0 0 4 20.5V5.5Z" />
                <path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H19v3H6.5A2.5 2.5 0 0 1 4 20.5Z" />
                <line x1="8" y1="8" x2="15" y2="8" stroke-linecap="round" />
              </template>
              <template v-else-if="kindOf(pub.title).icon === 'study'">
                <circle cx="11" cy="11" r="6.5" />
                <line x1="20" y1="20" x2="15.8" y2="15.8" stroke-linecap="round" />
                <path d="M8.5 11.5l1.8 1.8 3.3-3.6" stroke-linecap="round" stroke-linejoin="round" />
              </template>
              <template v-else-if="kindOf(pub.title).icon === 'manual'">
                <rect x="4" y="3" width="16" height="18" rx="2" />
                <line x1="8" y1="8" x2="16" y2="8" stroke-linecap="round" />
                <line x1="8" y1="12" x2="16" y2="12" stroke-linecap="round" />
                <line x1="8" y1="16" x2="13" y2="16" stroke-linecap="round" />
              </template>
              <template v-else-if="kindOf(pub.title).icon === 'report'">
                <path d="M6 3h9l3 3v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
                <path d="M15 3v3a1 1 0 0 0 1 1h3" />
                <path d="M8.5 17v-3M12 17v-6M15.5 17v-4" stroke-linecap="round" />
              </template>
              <template v-else-if="kindOf(pub.title).icon === 'profile'">
                <circle cx="12" cy="12" r="8.5" />
                <ellipse cx="12" cy="12" rx="4" ry="8.5" />
                <line x1="3.5" y1="12" x2="20.5" y2="12" />
              </template>
              <template v-else>
                <path d="M6 3h9l3 3v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
                <path d="M15 3v3a1 1 0 0 0 1 1h3" />
                <line x1="8" y1="12" x2="16" y2="12" />
                <line x1="8" y1="16" x2="16" y2="16" />
              </template>
            </svg>
          </span>
          <div class="publication-card__body">
            <span v-if="kindOf(pub.title).label" class="publication-card__kind">{{ kindOf(pub.title).label }}</span>
            <h3>{{ pub.title }}</h3>
            <p class="publication-card__meta">
              <span v-if="pub.dateLabel">{{ pub.dateLabel }} · </span>{{ formatSize(pub.sizeKb) }}
            </p>
          </div>
          <div class="publication-card__actions">
            <button type="button" class="btn btn--ghost" @click="openPreview(pub)">{{ t('publications.preview') }}</button>
            <a class="btn btn--primary" :href="pub.file" target="_blank" rel="noopener" download>
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M12 3v12m0 0-4-4m4 4 4-4M4 20h16" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              {{ t('publications.download') }}
            </a>
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
          <p v-if="previewDoc.dateLabel">{{ previewDoc.dateLabel }}</p>
        </div>
        <div class="preview-modal__actions">
          <a class="btn btn--primary" :href="previewDoc.file" target="_blank" rel="noopener" download>{{ t('publications.download') }}</a>
          <button type="button" class="icon-btn preview-modal__close" :title="t('publications.close')" @click="closePreview">
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
.publikacije-hero {
  padding-bottom: var(--space-4);
}

.publikacije-hero__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
}

.publikacije-hero__text {
  min-width: 0;
}

.publikacije-hero__illustration {
  flex-shrink: 0;
  width: min(300px, 32vw);
  height: auto;
}

/* The drawing is decoration; below the breakpoint the words need the room. */
@media (max-width: 820px) {
  .publikacije-hero__illustration {
    display: none;
  }
}

.publikacije-hero__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  max-width: 640px;
  margin-top: var(--space-3);
}

.publikacije-grid {
  display: grid;
  gap: var(--space-4);
}

/* Two columns once there is room; eight full-width bands made the page feel
   longer and emptier than it is. Each card turns into a vertical stack at the
   same breakpoint -- kept horizontal, the title had only a third of the card's
   width left and wrapped to seven lines. Actions are pushed to the bottom so
   the buttons line up across a row whatever the title length. */
@media (min-width: 1100px) {
  .publikacije-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: stretch;
  }

  .publikacije-grid .publication-card {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
    height: 100%;
  }

  .publikacije-grid .publication-card__actions {
    width: 100%;
    margin-top: auto;
  }

  .publikacije-grid .publication-card__actions .btn {
    flex: 1;
    justify-content: center;
  }
}

.publication-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.publication-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.publication-card__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  background: var(--kind-bg, var(--color-primary-light));
  color: var(--kind-fg, var(--color-primary));
}

/* One hue per document kind. They stay inside the site's green-forward family
   -- these are accents on a card, not a second brand palette. */
.publication-card--guide { --kind-bg: #e9f7ec; --kind-fg: #2f8f45; --kind-rule: #42b758; }
.publication-card--study { --kind-bg: #e6f2f6; --kind-fg: #24707f; --kind-rule: #3596a8; }
.publication-card--manual { --kind-bg: #edf0fb; --kind-fg: #45539c; --kind-rule: #6675c4; }
.publication-card--report { --kind-bg: #fbf1e4; --kind-fg: #94682a; --kind-rule: #c08a37; }
.publication-card--profile { --kind-bg: #f2ecf7; --kind-fg: #6a4a8c; --kind-rule: #8b66b0; }
.publication-card--doc { --kind-bg: var(--color-bg-alt); --kind-fg: var(--color-text-muted); --kind-rule: var(--color-border); }

/* A thin coloured edge repeats the kind at a glance down the column. */
.publication-card {
  border-left: 3px solid var(--kind-rule, var(--color-border));
}

.publication-card__kind {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--kind-fg, var(--color-text-muted));
  background: var(--kind-bg, var(--color-bg-alt));
  border-radius: 999px;
  padding: 3px 9px;
  margin-bottom: 6px;
}

.publication-card__icon svg {
  width: 28px;
  height: 28px;
}

.publication-card__body {
  flex: 1;
  min-width: 0;
}

.publication-card__body h3 {
  margin: 0;
}

.publication-card__meta {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-top: 4px;
}

.publication-card__actions {
  flex-shrink: 0;
  display: flex;
  gap: 10px;
}

.btn--ghost {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-ink);
}

.btn--ghost:hover {
  background: var(--color-bg-alt);
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

@media (max-width: 560px) {
  .publication-card {
    flex-direction: column;
    text-align: center;
  }

  .publication-card__actions {
    width: 100%;
  }

  .publication-card__actions .btn {
    flex: 1;
    justify-content: center;
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
</style>
