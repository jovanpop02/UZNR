<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import YoutubeSection from '../components/YoutubeSection.vue'
import MediaSlider from '../components/MediaSlider.vue'
import { pressClippings as bundledClippings } from '../data/press'
import { text, usePageSections, withFallback } from '../cms'
import { posts } from '../data/instagram'
import logo from '../assets/uznr-logo.png'

const { t, locale } = useI18n()

// Editable under Stranice → Press / Mediji.
const sections = usePageSections('press')
const pressClippings = withFallback(sections, bundledClippings, (cmsSections) =>
  cmsSections.flatMap((section) =>
    section.items.map((item) => ({
      title: text(item.title, locale.value),
      source: text(item.reference, locale.value),
      date: item.date_label || '',
      thumb: item.image || '',
      href: item.href || '',
    }))
  )
)

const INSTAGRAM_URL = 'https://www.instagram.com/uznr.me/'
const FACEBOOK_URL = 'https://www.facebook.com/uznr.me'

const socials = [
  { label: 'Facebook', href: FACEBOOK_URL, icon: 'facebook' },
  { label: 'Instagram', href: INSTAGRAM_URL, icon: 'instagram' },
  { label: 'YouTube', href: 'https://www.youtube.com/@udruzenjezastitenaraducrne2151', icon: 'youtube' },
]

// The source list is already ordered newest-first, so group positionally rather
// than by sorting: open a new year heading whenever a dated clipping moves into
// a different year. A handful carry no date at all — those stay where they sit
// instead of being collected into a trailing bucket, which would have pushed the
// newest coverage to the bottom of the page.
// The newest clipping is pulled out as a full-width lead card.
const lead = computed(() => pressClippings.value[0])
const rest = computed(() => pressClippings.value.slice(1))

const yearOf = (item) => (item.date ? item.date.split('.').pop() : '')

// Year headings left 1- and 2-card rows stranded in a 4-across grid. Filtering
// instead keeps every row full, and matches how ArhivaPage already lets people
// narrow by year.
const years = computed(() =>
  [...new Set(rest.value.map(yearOf).filter(Boolean))].sort((a, b) => b - a)
)

const selectedYear = ref('all')

const filtered = computed(() =>
  selectedYear.value === 'all'
    ? rest.value
    : rest.value.filter((item) => yearOf(item) === selectedYear.value)
)

// Instagram embeds have no intrinsic height and vary by post type — a carousel
// runs ~180px taller than a single image. Each embed posts its measured height
// to the parent window, so listen for that to find out how tall each one wants
// to be.
const FALLBACK_HEIGHT = 720
const frames = ref([])
const igSlider = ref(null)

// Every slide shares one height, so the row reads as a set of equal cards
// rather than a ragged line, and the tallest embed sets it: anything shorter
// would crop the taller posts, and a cropped embed can't be scrolled to recover
// what's cut (scrolling="no", and it's cross-origin).
//
// This is a high-water mark, not a max over the current measurements. Embeds
// re-measure repeatedly as they settle and often report a SMALLER height the
// second time — a carousel reports whichever slide is showing, and captions
// collapse once the fonts land. Taking the live maximum meant the whole row
// visibly shrank while you were looking at it. Holding the tallest value ever
// seen means the cards only ever grow, and then stay put.
//
// The fallback is a guess for the pre-measurement paint, so it must not act as
// the floor of that mark: if every post really is shorter than the guess, the
// row would keep the guess forever and carry dead space. The first real
// measurement therefore replaces it outright, and only later ones compete.
const slideHeight = ref(FALLBACK_HEIGHT)
let measured = false

// Instagram's embeds ignore loading="lazy" — measured, they pulled ~13 MB over
// 113 requests on first paint of this page, before anyone scrolled near them.
// So keep them out of the DOM until the section is actually approaching the
// viewport, and mount them only then.
const igSection = ref(null)
const igVisible = ref(false)
let igObserver = null

function onMessage(event) {
  if (event.origin !== 'https://www.instagram.com') return
  let data = event.data
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data)
    } catch {
      return
    }
  }
  const height = data?.details?.height
  if (data?.type !== 'MEASURE' || !height) return
  // Only accept a measurement from one of our own frames.
  const i = frames.value.findIndex((f) => f && f.contentWindow === event.source)
  if (i === -1) return

  const next = Math.ceil(height)
  if (measured && next <= slideHeight.value) return
  measured = true
  slideHeight.value = next
  // Resizing the slides changes the track, so let the slider recheck its arrows.
  nextTick(() => igSlider.value?.update())
}

onMounted(() => {
  window.addEventListener('message', onMessage)

  if (typeof IntersectionObserver === 'undefined') {
    igVisible.value = true
    return
  }
  igObserver = new IntersectionObserver(
    (entries) => {
      if (!entries.some((e) => e.isIntersecting)) return
      igVisible.value = true
      igObserver.disconnect()
    },
    { rootMargin: '300px 0px' },
  )
  igObserver.observe(igSection.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('message', onMessage)
  igObserver?.disconnect()
})
</script>

<template>
  <div class="press">
    <section class="section press__intro">
      <div class="container">
        <h1>{{ t('press.title') }}</h1>
        <p class="press__lead">
          {{ t('press.leadBefore') }}
          <a class="press__email" href="mailto:info@uznr.me">info@uznr.me</a>{{ t('press.leadAfter') }}
        </p>

        <div class="press__social">
          <a v-for="s in socials" :key="s.label" :href="s.href" target="_blank" rel="noopener" class="press__social-link">
            <svg v-if="s.icon === 'facebook'" viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M14 9h3V5h-3c-2.2 0-4 1.8-4 4v2H8v4h2v7h4v-7h3l1-4h-4v-2c0-.6.4-1 1-1z"/></svg>
            <svg v-else-if="s.icon === 'instagram'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>
            <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><rect x="2" y="6" width="20" height="12" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.5l6 2.5-6 2.5z"/></svg>
            {{ s.label }}
          </a>
        </div>
      </div>
    </section>

    <YoutubeSection />

    <section ref="igSection" class="section press__ig-section">
      <div class="container">
        <header v-reveal class="ig__head">
          <div>
            <span class="ig__badge">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true">
                <rect x="3" y="3" width="18" height="18" rx="5" />
                <circle cx="12" cy="12" r="4.2" />
                <circle cx="17.2" cy="6.8" r="1.1" fill="currentColor" stroke="none" />
              </svg>
              Instagram
            </span>
            <h2 class="ig__title">{{ t('press.instagramTitle') }}</h2>
            <p class="ig__text">{{ t('press.instagramText') }}</p>
          </div>

          <div class="ig__profile">
            <img class="ig__avatar" :src="logo" alt="" width="120" height="60" />
            <span class="ig__profile-meta">
              <span class="ig__handle">@uznr.me</span>
              <span class="ig__org">{{ t('press.instagramOrg') }}</span>
            </span>
            <a class="ig__btn" :href="INSTAGRAM_URL" target="_blank" rel="noopener">
              {{ t('press.instagramBtn') }}
            </a>
          </div>
        </header>

        <MediaSlider
          ref="igSlider"
          class="ig__slider"
          :prev-label="t('slider.prev')"
          :next-label="t('slider.next')"
        >
          <li v-for="(post, i) in posts" :key="post.code" class="ig__slide">
            <iframe
              v-if="igVisible"
              :ref="(el) => (frames[i] = el)"
              :src="`https://www.instagram.com/p/${post.code}/embed/`"
              :title="`${t('press.instagramTitle')} — @uznr.me`"
              :style="{ height: slideHeight + 'px' }"
              loading="lazy"
              scrolling="no"
              allowtransparency
            ></iframe>
            <div v-else class="ig__placeholder" :style="{ height: slideHeight + 'px' }" aria-hidden="true"></div>
          </li>
        </MediaSlider>
      </div>
    </section>

    <section class="section section--alt press__portals">
      <div class="container">
        <h2 v-reveal class="section-title">{{ t('press.portalsTitle') }}</h2>
        <p v-reveal="1" class="press__portals-lead">{{ t('press.portalsText') }}</p>

        <a v-reveal="2" class="lead" :href="lead.href" target="_blank" rel="noopener">
          <span class="lead__media">
            <img :src="lead.thumb" :alt="lead.title" />
          </span>
          <span class="lead__body">
            <span class="lead__flag">{{ t('press.latest') }}</span>
            <span class="lead__title">{{ lead.title }}</span>
            <span class="lead__meta">
              <span class="lead__source">{{ lead.source }}</span>
              <span v-if="lead.date" class="lead__date">{{ lead.date }}</span>
            </span>
            <span class="lead__cta">
              {{ t('press.readAtSource') }}
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                <path d="M7 17L17 7M17 7H9M17 7v8" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </span>
          </span>
        </a>

        <div class="press__filters" role="group" :aria-label="t('press.filterLabel')">
          <button
            type="button"
            class="press__chip"
            :class="{ 'press__chip--on': selectedYear === 'all' }"
            :aria-pressed="selectedYear === 'all'"
            @click="selectedYear = 'all'"
          >
            {{ t('press.filterAll') }}
            <span class="press__chip-count">{{ rest.length }}</span>
          </button>
          <button
            v-for="year in years"
            :key="year"
            type="button"
            class="press__chip"
            :class="{ 'press__chip--on': selectedYear === year }"
            :aria-pressed="selectedYear === year"
            @click="selectedYear = year"
          >
            {{ year }}
          </button>
        </div>

        <div class="press__group">
          <ul class="press__clips">
            <li v-for="(item, i) in filtered" :key="item.href + i" v-reveal="i % 3">
              <a class="clip" :href="item.href" target="_blank" rel="noopener">
                <span class="clip__media">
                  <img :src="item.thumb" :alt="item.title" loading="lazy" />
                  <span class="clip__source">{{ item.source }}</span>
                </span>
                <span class="clip__body">
                  <span class="clip__title">{{ item.title }}</span>
                  <span class="clip__foot">
                    <span v-if="item.date" class="clip__date">{{ item.date }}</span>
                    <svg class="clip__arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                      <path d="M7 17L17 7M17 7H9M17 7v8" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </span>
                </span>
              </a>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.press__intro {
  padding-bottom: var(--space-6);
}

.press__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  max-width: 640px;
  margin-top: var(--space-3);
}

.press__email {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.press__email:hover {
  text-decoration: underline;
}

.press__social {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

.press__social-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  color: var(--color-ink);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.press__social-link:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

/* Instagram ---------------------------------------------------------- */

.ig__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-5);
}

/* Instagram's own gradient is kept to the badge glyph only — at panel scale it
   fought the green brand palette everywhere else on the site. */
.ig__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 14px;
  border-radius: 999px;
  background: linear-gradient(120deg, #7b2ff7 0%, #dc2743 55%, #f09433 100%);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
}

.ig__title {
  margin-top: var(--space-3);
}

.ig__text {
  margin-top: var(--space-2);
  max-width: 52ch;
  color: var(--color-text-muted);
}

.ig__profile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  box-shadow: var(--shadow-sm);
}

/* The mark is a wide wordmark, so a circular crop would shrink it to nothing. */
.ig__avatar {
  flex: 0 0 auto;
  width: 120px;
  height: 60px;
  object-fit: contain;
}

.ig__profile-meta {
  display: grid;
  gap: 2px;
}

.ig__handle {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-ink);
}

.ig__org {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  max-width: 26ch;
}

.ig__btn {
  flex: 0 0 auto;
  padding: 10px 20px;
  border-radius: 999px;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  font-size: 0.88rem;
  text-decoration: none;
  transition: background 0.15s ease;
}

.ig__btn:hover {
  background: var(--color-primary-dark);
}

.ig__slide {
  width: 340px;
  max-width: 84vw;
}

.ig__placeholder {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
}

.ig__slider iframe {
  width: 100%;
  /* Height is set inline, one value shared by every slide; see the script. */
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  display: block;
  overflow: hidden;
  transition: height 0.2s ease;
}

/* Portali ------------------------------------------------------------ */

.press__portals-lead {
  color: var(--color-text-muted);
  max-width: 60ch;
  margin-top: calc(var(--space-5) * -1 + var(--space-1));
  margin-bottom: var(--space-5);
}

/* Lead clipping ------------------------------------------------------ */

.lead {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 6fr);
  align-items: stretch;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  text-decoration: none;
  color: var(--color-ink);
  margin-bottom: var(--space-6);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.lead:hover {
  transform: translateY(-3px);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.lead__media {
  display: block;
  overflow: hidden;
  background: var(--color-bg-alt);
  min-height: 260px;
}

.lead__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.lead:hover .lead__media img {
  transform: scale(1.03);
}

.lead__body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-5);
}

.lead__flag {
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
}

.lead__title {
  font-size: clamp(1.15rem, 1rem + 0.7vw, 1.6rem);
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: -0.2px;
}

.lead:hover .lead__title {
  color: var(--color-primary-dark);
}

.lead__meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.lead__source {
  font-weight: 700;
  color: var(--color-primary-dark);
}

.lead__date {
  font-variant-numeric: tabular-nums;
}

.lead__date::before {
  content: '·';
  margin-right: var(--space-2);
  color: var(--color-border);
}

.lead__cta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: auto;
  padding-top: var(--space-2);
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-primary-dark);
}

.lead:hover .lead__cta svg {
  transform: translate(2px, -2px);
}

.lead__cta svg {
  transition: transform 0.15s ease;
}

.press__filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.press__chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  color: var(--color-text);
  font: inherit;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.press__chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.press__chip--on {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.press__chip-count {
  font-size: 0.78rem;
  font-weight: 700;
  opacity: 0.7;
  font-variant-numeric: tabular-nums;
}

.press__clips {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-4);
}

.clip {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  text-decoration: none;
  color: var(--color-ink);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.clip:hover {
  transform: translateY(-3px);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.clip__media {
  position: relative;
  display: block;
  aspect-ratio: 16 / 10;
  background: var(--color-bg-alt);
  overflow: hidden;
}

.clip__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.clip:hover .clip__media img {
  transform: scale(1.04);
}

.clip__source {
  position: absolute;
  left: var(--space-2);
  bottom: var(--space-2);
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(23, 33, 28, 0.82);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.clip__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  flex: 1;
  padding: var(--space-3);
}

.clip__title {
  font-size: 0.95rem;
  font-weight: 600;
  line-height: 1.4;
  transition: color 0.15s ease;
}

.clip:hover .clip__title {
  color: var(--color-primary-dark);
}

.clip__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  margin-top: auto;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.clip__date {
  font-variant-numeric: tabular-nums;
}

.clip__arrow {
  margin-left: auto;
  color: var(--color-text-muted);
  transition: color 0.15s ease, transform 0.15s ease;
}

.clip:hover .clip__arrow {
  color: var(--color-primary);
  transform: translate(2px, -2px);
}

@media (max-width: 780px) {
  /* Side by side, the lead card squeezes its headline into a narrow column. */
  .lead {
    grid-template-columns: 1fr;
  }

  .lead__media {
    min-height: 0;
    aspect-ratio: 16 / 9;
  }

  .lead__body {
    padding: var(--space-4);
  }
}

@media (max-width: 700px) {
  .ig__profile {
    width: 100%;
    flex-wrap: wrap;
  }

  .ig__btn {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 600px) {
  .press__clips {
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: var(--space-3);
  }
}
</style>
