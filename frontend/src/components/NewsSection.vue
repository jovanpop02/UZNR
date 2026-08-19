<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchNews } from '../api'
import { localizeList } from '../cms'
import NewsCard from './NewsCard.vue'
import SkeletonBlock from './SkeletonBlock.vue'
import WakingNotice from './WakingNotice.vue'

const { t, locale } = useI18n()
const HOMEPAGE_LIMIT = 7

const news = ref([])
const loading = ref(true)
const error = ref(null)

const visibleNews = computed(() =>
  localizeList(news.value, locale.value).slice(0, HOMEPAGE_LIMIT)
)
const featuredNews = computed(() => visibleNews.value[0])
const restNews = computed(() => visibleNews.value.slice(1))

async function load() {
  loading.value = true
  error.value = null
  try {
    news.value = await fetchNews()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="news">
    <h2 v-reveal class="news__title">{{ t('newsSection.title') }}<span class="news__title-mark"></span></h2>
    <template v-if="loading">
      <SkeletonBlock variant="featured" />
      <div class="news__skeleton-grid">
        <SkeletonBlock variant="card" :count="3" />
      </div>
      <WakingNotice />
    </template>
    <div v-else-if="error" class="news__error">
      <p class="state-message state-message--error">{{ t('newsSection.error') }}</p>
      <button type="button" class="btn btn--primary" @click="load">{{ t('common.retry') }}</button>
    </div>
    <p v-else-if="!news.length" class="state-message">{{ t('newsSection.empty') }}</p>
    <template v-else>
      <div v-reveal class="news__featured">
        <NewsCard :item="featuredNews" featured />
      </div>
      <div v-reveal="1" class="news__grid">
        <NewsCard v-for="item in restNews" :key="item.slug" :item="item" />
      </div>
      <router-link v-reveal="2" class="news__more" to="/arhiva">{{ t('newsSection.viewAll') }}</router-link>
    </template>
  </div>
</template>

<style scoped>
.news__title {
  display: inline-block;
  margin-bottom: var(--space-4);
  position: relative;
}

.news__title-mark {
  display: block;
  width: 44px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-primary);
  margin-top: 10px;
}

.news__featured {
  margin-bottom: var(--space-4);
}

.news__skeleton-grid {
  margin-top: var(--space-4);
}

.news__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.news__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.news__more {
  display: inline-block;
  margin-top: var(--space-4);
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.news__more:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

@media (max-width: 900px) {
  .news__grid {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    margin-inline: calc(var(--space-4) * -1);
    padding-inline: var(--space-4);
    padding-bottom: var(--space-2);
  }

  .news__grid > * {
    flex: 0 0 78%;
    max-width: 320px;
    scroll-snap-align: start;
  }
}

@media (max-width: 600px) {
  .news__grid > * {
    flex-basis: 84%;
  }
}
</style>
