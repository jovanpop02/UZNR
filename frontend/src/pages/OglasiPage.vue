<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchAnnouncements } from '../api'
import { localizeList } from '../cms'
import AnnouncementCard from '../components/AnnouncementCard.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import WakingNotice from '../components/WakingNotice.vue'
import { splitExcerptForLink } from '../excerptLink'

const { t, locale } = useI18n()
const rawAnnouncements = ref([])
const announcements = computed(() => localizeList(rawAnnouncements.value, locale.value))
const loading = ref(true)
const error = ref(null)
const selected = ref(null)

const selectedExcerptParts = computed(() => (selected.value ? splitExcerptForLink(selected.value.excerpt, selected.value) : []))

async function load() {
  loading.value = true
  error.value = null
  try {
    rawAnnouncements.value = await fetchAnnouncements()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('sr-Latn-ME', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function openDetail(item) {
  selected.value = item
}

function closeDetail() {
  selected.value = null
}
</script>

<template>
  <div>
  <section class="section oglasi">
    <div class="container">
      <h1>{{ t('ads.title') }}</h1>

      <template v-if="loading">
        <SkeletonBlock variant="card" :count="3" />
        <WakingNotice />
      </template>
      <div v-else-if="error" class="oglasi__error">
        <p class="state-message state-message--error">{{ t('ads.error') }}</p>
        <button type="button" class="btn btn--primary" @click="load">{{ t('common.retry') }}</button>
      </div>
      <p v-else-if="!announcements.length" class="state-message">{{ t('ads.empty') }}</p>
      <template v-else>
        <AnnouncementCard :item="announcements[0]" featured class="oglasi__featured" @open="openDetail" />
        <div v-if="announcements.length > 1" class="oglasi__grid">
          <AnnouncementCard v-for="item in announcements.slice(1)" :key="item.id" :item="item" @open="openDetail" />
        </div>
      </template>
    </div>
  </section>

  <div v-if="selected" class="oglas-overlay" @click.self="closeDetail">
    <div class="oglas-modal">
      <button type="button" class="icon-btn oglas-modal__close" :title="t('ads.close')" @click="closeDetail">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
        </svg>
      </button>

      <div class="oglas-modal__thumb" :class="{ 'oglas-modal__thumb--empty': !selected.photo }">
        <span class="oglas-modal__status" :class="selected.is_open ? 'oglas-modal__status--open' : 'oglas-modal__status--closed'">
          {{ selected.is_open ? t('ads.statusOpen') : t('ads.statusClosed') }}
        </span>
        <img v-if="selected.photo" :src="selected.photo" :alt="selected.title" />
        <svg v-else class="oglas-modal__thumb-icon" viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <path d="M24 4 L40 10 V22 Q40 36 24 44 Q8 36 8 22 V10 Z" fill="currentColor" opacity="0.16" />
          <path d="M24 4 L40 10 V22 Q40 36 24 44 Q8 36 8 22 V10 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
          <path d="M16 23 L21 29 L33 15" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>

      <div class="oglas-modal__body">
        <time v-if="selected.date" class="oglas-modal__date" :datetime="selected.date">{{ formatDate(selected.date) }}</time>
        <h2 class="oglas-modal__title">{{ selected.title }}</h2>
        <p class="oglas-modal__excerpt">
          <template v-for="(part, i) in selectedExcerptParts" :key="i">
            <a v-if="part.isLink" :href="selected.link" target="_blank" rel="noopener" class="oglas-modal__inline-link">{{ part.text }}</a>
            <template v-else>{{ part.text }}</template>
          </template>
        </p>

        <div v-if="selected.links?.length" class="oglas-modal__docs">
          <a
            v-for="doc in selected.links"
            :key="doc.title"
            class="oglas-modal__doc"
            :href="doc.href"
            target="_blank"
            rel="noopener"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M12 3v12m0 0-4-4m4 4 4-4M4 20h16" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            {{ doc.title }}
          </a>
        </div>
      </div>
    </div>
  </div>

  <section id="priprema" class="section oglasi__priprema">
    <div class="container oglasi__priprema-inner">
      <span class="oglasi__priprema-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M12 3 4 6v6c0 5 3.5 8.5 8 9 4.5-.5 8-4 8-9V6Z" stroke-linejoin="round" />
          <path d="M8.5 12.2 11 14.7l4.8-5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </span>
      <h2 class="uppercase">{{ t('ads.preparationTitle') }}</h2>
      <p class="oglasi__priprema-text">
        {{ t('ads.preparationText') }}
      </p>
      <div class="oglasi__priprema-actions">
        <a class="btn btn--primary" href="mailto:info@uznr.me">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <rect x="3" y="5" width="18" height="14" rx="2.5" />
            <path d="m4 7 8 6 8-6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          {{ t('ads.sendInquiry') }}
        </a>
        <a class="oglasi__priprema-phone" href="tel:+38267412900">067 412 900</a>
      </div>
    </div>
  </section>
  </div>
</template>

<style scoped>
.oglasi__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.oglasi__featured {
  margin-top: var(--space-4);
}

.oglasi__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-top: var(--space-4);
}

@media (max-width: 700px) {
  .oglasi__grid {
    grid-template-columns: 1fr;
  }
}

.oglasi__priprema {
  background: var(--color-bg-alt);
  text-align: center;
}

.oglasi__priprema-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.oglasi__priprema-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: var(--space-3);
}

.oglasi__priprema-icon svg {
  width: 28px;
  height: 28px;
}

.oglasi__priprema h2 {
  max-width: 720px;
}

.oglasi__priprema-text {
  max-width: 640px;
  color: var(--color-text-muted);
  margin-top: var(--space-3);
}

.oglasi__priprema-actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-top: var(--space-5);
}

.oglasi__priprema-phone {
  color: var(--color-ink);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid var(--color-border);
}

.oglasi__priprema-phone:hover {
  border-color: var(--color-ink);
}

@media (max-width: 480px) {
  .oglasi__priprema-actions {
    flex-direction: column;
    gap: var(--space-3);
  }
}

.oglas-overlay {
  position: fixed;
  inset: 0;
  background: rgba(23, 33, 28, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  z-index: 100;
  overflow-y: auto;
}

.oglas-modal {
  position: relative;
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin-block: auto;
}

.oglas-modal__close {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  z-index: 1;
  background: rgba(255, 255, 255, 0.9);
}

.oglas-modal__thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: var(--color-primary-light);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  overflow: hidden;
}

.oglas-modal__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.oglas-modal__thumb--empty {
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-bg-alt));
  display: flex;
  align-items: center;
  justify-content: center;
}

.oglas-modal__thumb-icon {
  width: 72px;
  height: 72px;
  color: var(--color-primary);
  opacity: 0.55;
}

.oglas-modal__status {
  position: absolute;
  top: 14px;
  left: 14px;
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.oglas-modal__status--open {
  background: rgba(66, 183, 88, 0.92);
  color: #fff;
}

.oglas-modal__status--closed {
  background: rgba(23, 33, 28, 0.55);
  color: #fff;
}

.oglas-modal__body {
  padding: var(--space-5);
}

.oglas-modal__date {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: var(--space-2);
}

.oglas-modal__title {
  margin-bottom: var(--space-3);
}

.oglas-modal__excerpt {
  color: var(--color-text-muted);
  white-space: pre-line;
  margin-bottom: var(--space-4);
}

.oglas-modal__inline-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.oglas-modal__inline-link:hover {
  color: var(--color-primary-dark);
}

.oglas-modal__docs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.oglas-modal__doc {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-ink);
  font-weight: 600;
  font-size: 0.92rem;
  text-decoration: none;
}

.oglas-modal__doc svg {
  flex-shrink: 0;
  color: var(--color-primary);
}

.oglas-modal__doc:hover {
  color: var(--color-primary);
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
  transition: background 0.15s ease, color 0.15s ease;
}

.icon-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

@media (max-width: 560px) {
  .oglas-modal {
    max-height: 95vh;
  }
}
</style>
