<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { fetchAnnouncements, fetchNews } from '../api'
import { localizeList } from '../cms'
import { announcementsToSearchIndex, buildStaticSearchIndex, foldSearchText } from '../search'
import NewsCard from '../components/NewsCard.vue'
import SafetyIllustration from '../components/SafetyIllustration.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import WakingNotice from '../components/WakingNotice.vue'

const { t, locale } = useI18n()
const route = useRoute()

const news = ref([])
const otherIndex = ref([])
const loading = ref(true)
const error = ref(null)

const selectedYear = ref('all')
const searchText = ref(typeof route.query.q === 'string' ? route.query.q : '')

const years = computed(() => {
  const set = new Set(news.value.map((item) => new Date(item.date).getFullYear()))
  return Array.from(set).sort((a, b) => b - a)
})

const filteredNews = computed(() => {
  let result = news.value
  if (selectedYear.value !== 'all') {
    result = result.filter((item) => new Date(item.date).getFullYear() === Number(selectedYear.value))
  }
  const q = foldSearchText(searchText.value.trim())
  if (q) {
    result = result.filter((item) =>
      foldSearchText(item.title).includes(q) || foldSearchText(item.excerpt).includes(q)
    )
  }
  return result
})

const otherResults = computed(() => {
  const q = foldSearchText(searchText.value.trim())
  if (!q) return []
  return otherIndex.value.filter((item) => foldSearchText(item.title).includes(q))
})

function formatSize(sizeKb) {
  if (!sizeKb) return null
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}

async function load() {
  loading.value = true
  error.value = null
  otherIndex.value = buildStaticSearchIndex()
  try {
    const [newsData, announcements] = await Promise.all([fetchNews(), fetchAnnouncements()])
    // The archive searches over titles and excerpts, so it needs the text
    // resolved to the language on screen rather than the `{ mne, en }` pair.
    news.value = localizeList(newsData, locale.value)
    otherIndex.value = [
      ...otherIndex.value,
      ...announcementsToSearchIndex(localizeList(announcements, locale.value)),
    ]
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="section arhiva">
    <div class="container">
      <h1>{{ t('archive.title') }}</h1>

      <div v-if="!loading && news.length" class="arhiva__toolbar">
        <div class="arhiva__search">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2" stroke-linecap="round"/></svg>
          <input v-model="searchText" type="search" :placeholder="t('archive.searchPlaceholder')" :aria-label="t('archive.searchAriaLabel')" />
        </div>
        <label class="arhiva__filter-label" for="arhiva-year">{{ t('archive.yearLabel') }}</label>
        <select id="arhiva-year" class="arhiva__select" v-model="selectedYear">
          <option value="all">{{ t('archive.yearAll') }}</option>
          <option v-for="year in years" :key="year" :value="String(year)">{{ year }}</option>
        </select>
      </div>

      <template v-if="loading">
        <SkeletonBlock variant="card" :count="6" />
        <WakingNotice />
      </template>
      <div v-else-if="error" class="arhiva__error">
        <p class="state-message state-message--error">{{ t('archive.error') }}</p>
        <button type="button" class="btn btn--primary" @click="load">{{ t('common.retry') }}</button>
      </div>
      <div v-else-if="!filteredNews.length" class="arhiva__empty">
        <SafetyIllustration variant="empty-archive" class="arhiva__empty-illustration" />
        <p class="arhiva__empty-text">{{ t('archive.emptyText') }}</p>
      </div>
      <div v-else class="arhiva__grid">
        <NewsCard v-for="item in filteredNews" :key="item.slug" :item="item" />
      </div>

      <div v-if="otherResults.length" class="arhiva__other">
        <h2 class="arhiva__other-title">{{ t('archive.otherResultsTitle') }}</h2>
        <div class="arhiva__other-list">
          <div v-for="(item, i) in otherResults" :key="item.type + item.title + i" class="other-result">
            <span class="other-result__badge">{{ item.typeLabel }}</span>
            <div class="other-result__body">
              <p class="other-result__title">{{ item.title }}</p>
              <p v-if="item.meta || item.sizeKb" class="other-result__meta">
                <template v-if="item.meta">{{ item.meta }}</template>
                <template v-if="item.meta && formatSize(item.sizeKb)"> · </template>
                <template v-if="formatSize(item.sizeKb)">{{ formatSize(item.sizeKb) }}</template>
              </p>
            </div>
            <a v-if="item.file" class="other-result__action" :href="item.file" target="_blank" rel="noopener" download>{{ t('archive.download') }}</a>
            <router-link v-else class="other-result__action" :to="item.routeTo">{{ t('archive.open') }}</router-link>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.arhiva__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.arhiva__toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin: var(--space-4) 0 var(--space-5);
}

.arhiva__search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 220px;
  max-width: 340px;
  padding: 9px 14px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  transition: border-color 0.15s ease;
}

.arhiva__search:focus-within {
  border-color: var(--color-primary);
}

.arhiva__search input {
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.9rem;
  color: var(--color-ink);
  width: 100%;
}

.arhiva__filter-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text);
}

.arhiva__select {
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-family: inherit;
  color: var(--color-ink);
  background: var(--color-bg);
  cursor: pointer;
}

.arhiva__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-6) 0;
}

.arhiva__empty-illustration {
  max-width: 260px;
  margin-bottom: var(--space-3);
}

.arhiva__empty-text {
  color: var(--color-text-muted);
}

.arhiva__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

@media (max-width: 900px) {
  .arhiva__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .arhiva__grid {
    grid-template-columns: 1fr;
  }
}

.arhiva__other {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--color-border);
}

.arhiva__other-title {
  font-size: 1.1rem;
  margin-bottom: var(--space-3);
}

.arhiva__other-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.other-result {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
}

.other-result__badge {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.other-result__body {
  flex: 1;
  min-width: 0;
}

.other-result__title {
  font-weight: 600;
  font-size: 0.92rem;
}

.other-result__meta {
  color: var(--color-text-muted);
  font-size: 0.78rem;
  margin-top: 2px;
}

.other-result__action {
  flex-shrink: 0;
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.85rem;
  text-decoration: none;
}

.other-result__action:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .other-result {
    flex-wrap: wrap;
  }

  .other-result__body {
    flex-basis: 100%;
    order: 2;
  }

  .other-result__action {
    order: 1;
    margin-left: auto;
  }
}
</style>
