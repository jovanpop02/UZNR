<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { fetchNewsItem } from '../api'
import { localizeItem } from '../cms'
import { normalizeTitle } from '../text'
import SafetyIllustration from '../components/SafetyIllustration.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import WakingNotice from '../components/WakingNotice.vue'

const LONGFORM_THRESHOLD = 900

const { t, locale } = useI18n()
const route = useRoute()

const rawItem = ref(null)
const item = computed(() =>
  rawItem.value ? localizeItem(rawItem.value, locale.value) : null
)
const title = computed(() => normalizeTitle(item.value?.title))
const loading = ref(true)
const notFound = ref(false)
const error = ref(null)
const lightboxIndex = ref(null)

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('sr-Latn-ME', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

async function load(slug) {
  loading.value = true
  notFound.value = false
  error.value = null
  lightboxIndex.value = null
  try {
    rawItem.value = await fetchNewsItem(slug)
  } catch (e) {
    // Match on the status now that the API layer reports one — the old
    // substring check on the message also fired for any slug containing "404".
    if (e.status === 404) {
      notFound.value = true
    } else {
      error.value = e.message
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.slug))
watch(() => route.params.slug, (slug) => load(slug))

const bodyText = computed(() => item.value?.content || item.value?.excerpt || '')
const isLongForm = computed(() => bodyText.value.length > LONGFORM_THRESHOLD)

// The body is plain text, one paragraph per line, but articles imported from
// the old site carry bulleted lines (schools visited, speakers, recommendations).
// Rendered as ordinary paragraphs those read as a run of stray sentences, so
// consecutive bullets are grouped into a single list block instead.
const blocks = computed(() => {
  const out = []
  for (const line of bodyText.value.split('\n')) {
    const text = line.trim()
    if (!text) continue

    const bullet = text.match(/^[•·*-]\s+(.*)$/)
    if (bullet) {
      const last = out[out.length - 1]
      if (last?.type === 'list') last.items.push(bullet[1])
      else out.push({ type: 'list', items: [bullet[1]] })
    } else {
      out.push({ type: 'text', text })
    }
  }
  return out
})

const readingTime = computed(() => {
  const words = bodyText.value.trim().split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.round(words / 190))
})

// Every photo goes in the gallery below the text. Floating one into the middle
// of the article was a magazine flourish that only read well on the short stubs
// the page was first built against; with full-length articles it landed at a
// different point in every piece and made the set look inconsistent.
const gridImages = computed(() => item.value?.images ?? [])

const lightboxPhotos = computed(() => {
  const arr = []
  if (item.value?.thumbnail) arr.push(item.value.thumbnail)
  if (item.value?.images) arr.push(...item.value.images.map((img) => img.image))
  return arr
})

function openLightboxFor(url) {
  const idx = lightboxPhotos.value.indexOf(url)
  if (idx !== -1) lightboxIndex.value = idx
}

function closeLightbox() {
  lightboxIndex.value = null
}

function showNext() {
  if (lightboxIndex.value === null) return
  lightboxIndex.value = (lightboxIndex.value + 1) % lightboxPhotos.value.length
}

function showPrev() {
  if (lightboxIndex.value === null) return
  lightboxIndex.value = (lightboxIndex.value - 1 + lightboxPhotos.value.length) % lightboxPhotos.value.length
}

function onKeydown(e) {
  if (lightboxIndex.value === null) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowRight') showNext()
  else if (e.key === 'ArrowLeft') showPrev()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <article class="section news-detail">
    <div class="container news-detail__inner" :class="{ 'news-detail__inner--wide': isLongForm && item }">
      <router-link class="news-detail__back" to="/arhiva">{{ t('newsDetail.back') }}</router-link>

      <template v-if="loading">
        <SkeletonBlock variant="featured" />
        <WakingNotice />
      </template>

      <div v-else-if="notFound" class="news-detail__empty">
        <SafetyIllustration variant="not-found" class="news-detail__empty-illustration" />
        <h1 class="news-detail__empty-title">{{ t('newsDetail.notFoundTitle') }}</h1>
        <p class="news-detail__empty-text">{{ t('newsDetail.notFoundText') }}</p>
        <router-link class="btn btn--primary" to="/arhiva">{{ t('newsDetail.backBtn') }}</router-link>
      </div>

      <div v-else-if="error" class="news-detail__error">
        <p class="state-message state-message--error">{{ t('newsDetail.error') }}</p>
        <button type="button" class="btn btn--primary" @click="load(route.params.slug)">{{ t('common.retry') }}</button>
      </div>

      <template v-else-if="item">
        <div class="news-detail__meta">
          <time class="news-detail__date" :datetime="item.date">{{ formatDate(item.date) }}</time>
          <span v-if="isLongForm" class="news-detail__reading-time">{{ readingTime }} {{ t('newsDetail.readingTime') }}</span>
        </div>
        <h1 class="news-detail__title">{{ title }}</h1>

        <button
          v-if="item.thumbnail"
          type="button"
          class="news-detail__image-btn"
          @click="openLightboxFor(item.thumbnail)"
          :aria-label="t('newsDetail.openImageAriaLabel')"
        >
          <img class="news-detail__image" :src="item.thumbnail" :alt="item.title" />
        </button>

        <div class="news-detail__body" :class="{ 'news-detail__body--longform': isLongForm }">
          <template v-for="(block, i) in blocks" :key="i">
            <ul v-if="block.type === 'list'" class="news-detail__list">
              <li v-for="(entry, j) in block.items" :key="j">{{ entry }}</li>
            </ul>
            <p v-else>{{ block.text }}</p>
          </template>
        </div>

        <div v-if="gridImages.length" class="news-detail__gallery">
          <button
            v-for="(img, i) in gridImages"
            :key="i"
            type="button"
            class="news-detail__gallery-item"
            @click="openLightboxFor(img.image)"
            :aria-label="t('newsDetail.galleryPhotoAriaLabel', { n: i + 1 })"
          >
            <img :src="img.image" :alt="`${item.title} — fotografija ${i + 1}`" loading="lazy" />
          </button>
        </div>
      </template>
    </div>

    <Teleport to="body">
      <div
        v-if="lightboxIndex !== null"
        class="lightbox"
        role="dialog"
        aria-modal="true"
        @click.self="closeLightbox"
      >
        <button type="button" class="lightbox__close" @click="closeLightbox" :aria-label="t('newsDetail.close')">✕</button>

        <button
          v-if="lightboxPhotos.length > 1"
          type="button"
          class="lightbox__nav lightbox__nav--prev"
          @click.stop="showPrev"
          :aria-label="t('newsDetail.prevPhoto')"
        >
          ‹
        </button>

        <img class="lightbox__image" :src="lightboxPhotos[lightboxIndex]" :alt="item?.title" />

        <button
          v-if="lightboxPhotos.length > 1"
          type="button"
          class="lightbox__nav lightbox__nav--next"
          @click.stop="showNext"
          :aria-label="t('newsDetail.nextPhoto')"
        >
          ›
        </button>

        <p v-if="lightboxPhotos.length > 1" class="lightbox__counter">
          {{ lightboxIndex + 1 }} / {{ lightboxPhotos.length }}
        </p>
      </div>
    </Teleport>
  </article>
</template>

<style scoped>
.news-detail__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.news-detail__inner {
  max-width: 700px;
  transition: max-width 0.2s ease;
}

.news-detail__inner--wide {
  max-width: 900px;
}

.news-detail__back {
  display: inline-block;
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: var(--space-4);
}

.news-detail__back:hover {
  text-decoration: underline;
}

.news-detail__meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.news-detail__date {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.news-detail__reading-time {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  padding-left: var(--space-3);
  border-left: 1px solid var(--color-border);
}

.news-detail__title {
  margin-bottom: var(--space-4);
}

.news-detail__image-btn {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  cursor: zoom-in;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.news-detail__image-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.news-detail__image {
  width: 100%;
  display: block;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  transition: transform 0.3s ease;
}

.news-detail__image-btn:hover .news-detail__image {
  transform: scale(1.015);
}

.news-detail__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  color: var(--color-text);
  font-size: 1.02rem;
  line-height: 1.65;
}

/* Every paragraph is set identically. The first line used to be given extra
   size, weight and a darker ink as a longform accent, which worked while
   almost every item was a two-line stub. Once the articles carried their full
   text it applied to most of them, so the body read as two different colours
   of text rather than as a deliberate lead. */

/* Bulleted runs imported from the old site — school lists, speakers,
   recommendations. Markers sit in the gutter so the text block keeps the same
   left edge as the surrounding paragraphs. */
.news-detail__list {
  margin: 0;
  padding-left: 1.15em;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.news-detail__list li {
  padding-left: 0.15em;
}

.news-detail__list li::marker {
  color: var(--color-primary);
}

.news-detail__gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-2);
  margin-top: var(--space-5);
  clear: both;
}

.news-detail__gallery-item {
  display: block;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: var(--radius-sm, 8px);
  padding: 0;
  border: none;
  cursor: zoom-in;
  background: var(--color-bg-alt);
}

.news-detail__gallery-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.news-detail__gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.news-detail__gallery-item:hover img {
  transform: scale(1.05);
}

/* ---------- Not-found state ---------- */
.news-detail__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-6) 0;
}

.news-detail__empty-illustration {
  max-width: 280px;
  margin-bottom: var(--space-4);
}

.news-detail__empty-title {
  margin-bottom: var(--space-2);
}

.news-detail__empty-text {
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

/* ---------- Lightbox ---------- */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(15, 20, 17, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-5);
}

.lightbox__image {
  max-width: min(90vw, 1100px);
  max-height: 86vh;
  width: auto;
  height: auto;
  border-radius: var(--radius-sm);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.lightbox__close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.lightbox__close:hover {
  background: rgba(255, 255, 255, 0.22);
}

.lightbox__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  transition: background 0.15s ease;
}

.lightbox__nav:hover {
  background: rgba(255, 255, 255, 0.22);
}

.lightbox__nav--prev {
  left: var(--space-4);
}

.lightbox__nav--next {
  right: var(--space-4);
}

.lightbox__counter {
  position: absolute;
  bottom: var(--space-4);
  left: 50%;
  transform: translateX(-50%);
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.85rem;
  margin: 0;
}

@media (max-width: 600px) {
  .lightbox__nav {
    width: 40px;
    height: 40px;
    font-size: 1.4rem;
  }
}
</style>
