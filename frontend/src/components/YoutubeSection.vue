<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import logo from '../assets/uznr-logo.png'
import MediaSlider from './MediaSlider.vue'
import { channelId, videos } from '../data/youtube'

const { t, locale } = useI18n()

const CHANNEL_URL = 'https://www.youtube.com/@udruzenjezastitenaraducrne2151'
const SUBSCRIBE_URL = `https://www.youtube.com/channel/${channelId}?sub_confirmation=1`

const activeIndex = ref(0)
const active = computed(() => videos[activeIndex.value])

// Lite embed: until someone presses play we render just the poster frame, so a
// visit to this page costs one image rather than YouTube's whole player bundle
// (and its cookies). The real iframe is created on click, with autoplay set so
// the click that dismissed the poster also starts the video.
const playing = ref(false)

function play(index) {
  if (index !== undefined) activeIndex.value = index
  playing.value = true
}

// rel=0 no longer removes the end-screen suggestions, but since 2018 it does
// restrict them to this channel — which is what we want here. modestbranding
// keeps the player chrome quiet.
const embedSrc = computed(
  () => `https://www.youtube-nocookie.com/embed/${active.value.id}?rel=0&modestbranding=1&autoplay=1`
)

const thumb = (id) => `https://i.ytimg.com/vi/${id}/mqdefault.jpg`
const poster = (id) => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`

function formatDate(iso) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString(locale.value === 'en' ? 'en-GB' : 'sr-Latn-ME', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <section class="section yt">
    <div class="container">
      <header class="yt__head">
        <div>
          <span class="yt__badge">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
              <path d="M23 12s0-3.8-.5-5.6a2.9 2.9 0 0 0-2-2C18.7 4 12 4 12 4s-6.7 0-8.5.4a2.9 2.9 0 0 0-2 2C1 8.2 1 12 1 12s0 3.8.5 5.6a2.9 2.9 0 0 0 2 2C5.3 20 12 20 12 20s6.7 0 8.5-.4a2.9 2.9 0 0 0 2-2C23 15.8 23 12 23 12z"/>
              <path d="M10 15.5l6-3.5-6-3.5z" fill="#fff"/>
            </svg>
            YouTube
          </span>
          <h2 class="yt__title">{{ t('youtube.title') }}</h2>
          <p class="yt__lead">{{ t('youtube.lead') }}</p>
        </div>

        <div class="yt__channel">
          <img class="yt__avatar" :src="logo" alt="" width="76" height="48" />
          <span class="yt__channel-meta">
            <span class="yt__channel-name">{{ t('youtube.channelName') }}</span>
            <a class="yt__channel-sub" :href="SUBSCRIBE_URL" target="_blank" rel="noopener">
              {{ t('youtube.subscribe') }}
            </a>
          </span>
        </div>
      </header>

      <div v-reveal class="yt__stage">
        <iframe
          v-if="playing"
          :key="active.id"
          :src="embedSrc"
          :title="active.title"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>

        <button v-else type="button" class="yt__poster" :aria-label="`${t('youtube.playVideo')}: ${active.title}`" @click="play()">
          <img :src="poster(active.id)" :alt="active.title" width="480" height="360" />
          <span class="yt__poster-play" aria-hidden="true">
            <svg viewBox="0 0 68 48" width="68" height="48">
              <path d="M66.5 7.7a8.6 8.6 0 0 0-6-6C55.2 0 34 0 34 0S12.8 0 7.5 1.6a8.6 8.6 0 0 0-6 6A90 90 0 0 0 0 24a90 90 0 0 0 1.5 16.3 8.6 8.6 0 0 0 6 6C12.8 48 34 48 34 48s21.2 0 26.5-1.7a8.6 8.6 0 0 0 6-6A90 90 0 0 0 68 24a90 90 0 0 0-1.5-16.3z" fill="#f00"/>
              <path d="M27 34V14l18 10z" fill="#fff"/>
            </svg>
          </span>
        </button>
      </div>

      <p class="yt__now">{{ active.title }}</p>

      <MediaSlider
        class="yt__strip-wrap"
        dark
        :label="t('youtube.moreVideos')"
        :prev-label="t('slider.prev')"
        :next-label="t('slider.next')"
      >
        <li v-for="(v, i) in videos" :key="v.id" class="yt__slide">
          <button
            type="button"
            class="yt__card"
            :class="{ 'yt__card--active': i === activeIndex }"
            :aria-current="i === activeIndex"
            @click="play(i)"
          >
            <span class="yt__thumb">
              <img :src="thumb(v.id)" :alt="v.title" loading="lazy" width="320" height="180" />
              <span class="yt__play" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              </span>
            </span>
            <span class="yt__card-title">{{ v.title }}</span>
            <span class="yt__card-date">{{ formatDate(v.published) }}</span>
          </button>
        </li>
      </MediaSlider>

      <a class="yt__all" :href="CHANNEL_URL" target="_blank" rel="noopener">
        {{ t('youtube.visitChannel') }}
      </a>
    </div>
  </section>
</template>

<style scoped>
.yt {
  background: var(--color-ink);
  background-image: radial-gradient(circle at 12% 0%, rgba(66, 183, 88, 0.2), transparent 55%);
}

.yt__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.yt__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 14px 6px 10px;
  border-radius: 999px;
  background: #ff0000;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
}

.yt__title {
  color: #fff;
  margin-top: var(--space-3);
}

.yt__lead {
  color: rgba(255, 255, 255, 0.72);
  margin-top: var(--space-2);
  max-width: 56ch;
}

.yt__channel {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

/* The mark is a wide wordmark, so a circular crop would shrink it to nothing. */
.yt__avatar {
  flex: 0 0 auto;
  width: 76px;
  height: 48px;
  border-radius: var(--radius-sm);
  object-fit: contain;
  background: #fff;
  padding: 5px;
}

.yt__channel-meta {
  display: grid;
  gap: 3px;
}

.yt__channel-name {
  color: #fff;
  font-weight: 600;
  font-size: 0.92rem;
  line-height: 1.3;
  max-width: 24ch;
}

.yt__channel-sub {
  justify-self: start;
  padding: 5px 14px;
  border-radius: 999px;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.15s ease;
}

.yt__channel-sub:hover {
  background: var(--color-primary-dark);
}

/* Player ------------------------------------------------------------- */

.yt__stage {
  position: relative;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #000;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5);
}

.yt__stage iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}

.yt__poster {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  padding: 0;
  border: 0;
  background: #000;
  cursor: pointer;
  display: block;
}

.yt__poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.yt__poster-play {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}

.yt__poster-play svg {
  opacity: 0.9;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.yt__poster:hover .yt__poster-play svg,
.yt__poster:focus-visible .yt__poster-play svg {
  opacity: 1;
  transform: scale(1.08);
}

.yt__now {
  color: #fff;
  font-weight: 600;
  font-size: 1.05rem;
  margin-top: var(--space-4);
}

/* Strip -------------------------------------------------------------- */

.yt__strip-wrap {
  margin-top: var(--space-5);
}

.yt__slide {
  width: 232px;
}

.yt__card {
  display: grid;
  gap: 6px;
  width: 100%;
  height: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.82);
}

.yt__thumb {
  position: relative;
  display: block;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #000;
  border: 2px solid transparent;
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.yt__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.yt__card:hover .yt__thumb {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.4);
}

.yt__card--active .yt__thumb {
  border-color: var(--color-primary);
}

.yt__play {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  opacity: 0;
  transition: opacity 0.15s ease;
}

.yt__card:hover .yt__play,
.yt__card--active .yt__play {
  opacity: 1;
}

.yt__card-title {
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1.35;
  color: #fff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.yt__card--active .yt__card-title {
  color: var(--color-primary);
}

.yt__card-date {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.yt__all {
  display: inline-block;
  margin-top: var(--space-4);
  padding: 11px 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: background 0.15s ease;
}

.yt__all:hover {
  background: rgba(255, 255, 255, 0.12);
}

@media (max-width: 700px) {
  .yt__slide {
    width: 190px;
  }

  .yt__channel {
    width: 100%;
  }
}
</style>
