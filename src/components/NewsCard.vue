<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { normalizeTitle } from '../text'

const { t } = useI18n()

const props = defineProps({
  item: { type: Object, required: true },
  featured: { type: Boolean, default: false },
})

const linkTo = computed(() => `/vijesti/${props.item.slug}`)
const title = computed(() => normalizeTitle(props.item.title))

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('sr-Latn-ME', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}
</script>

<template>
  <router-link :to="linkTo" class="news-card" :class="{ 'news-card--featured': featured }">
    <div class="news-card__thumb" :class="{ 'news-card__thumb--empty': !item.thumbnail }">
      <img v-if="item.thumbnail" :src="item.thumbnail" :alt="title" loading="lazy" />
    </div>
    <div class="news-card__body">
      <span v-if="featured" class="news-card__badge">{{ t('newsCard.latest') }}</span>
      <time class="news-card__date" :datetime="item.date">{{ formatDate(item.date) }}</time>
      <h3 class="news-card__title">{{ title }}</h3>
      <p class="news-card__excerpt">{{ item.excerpt }}</p>
    </div>
  </router-link>
</template>

<style scoped>
.news-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.news-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.news-card__thumb {
  aspect-ratio: 16 / 9;
  background: var(--color-primary-light);
}

.news-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-card__thumb--empty {
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-bg-alt));
}

.news-card__body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.news-card__date {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.news-card__title {
  color: var(--color-ink);
}

.news-card__excerpt {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card--featured {
  flex-direction: row;
}

.news-card--featured .news-card__thumb {
  width: 52%;
  aspect-ratio: auto;
  flex-shrink: 0;
}

.news-card--featured .news-card__body {
  min-width: 0;
  padding: var(--space-5);
  gap: var(--space-2);
  justify-content: center;
}

.news-card__badge {
  display: inline-block;
  width: fit-content;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: var(--space-1);
}

.news-card--featured .news-card__title {
  font-size: 1.5rem;
  line-height: 1.25;
}

.news-card--featured .news-card__excerpt {
  font-size: 1rem;
  -webkit-line-clamp: 4;
}

@media (max-width: 700px) {
  .news-card--featured {
    flex-direction: column;
  }

  .news-card--featured .news-card__thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
  }
}

@media (max-width: 480px) {
  .news-card__body {
    padding: var(--space-3);
  }

  .news-card--featured .news-card__body {
    padding: var(--space-4);
  }

  .news-card--featured .news-card__title {
    font-size: 1.25rem;
  }
}
</style>
