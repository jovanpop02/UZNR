<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { splitExcerptForLink } from '../excerptLink'

const { t } = useI18n()

const props = defineProps({
  item: { type: Object, required: true },
  featured: { type: Boolean, default: false },
})

const emit = defineEmits(['open'])

const excerptParts = computed(() => splitExcerptForLink(props.item.excerpt, props.item))

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('sr-Latn-ME', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}
</script>

<template>
  <article
    class="announcement-card"
    :class="{ 'announcement-card--featured': featured }"
    role="button"
    tabindex="0"
    @click="emit('open', item)"
    @keydown.enter="emit('open', item)"
    @keydown.space.prevent="emit('open', item)"
  >
    <div class="announcement-card__thumb" :class="{ 'announcement-card__thumb--empty': !item.photo }">
      <span class="announcement-card__status" :class="item.is_open ? 'announcement-card__status--open' : 'announcement-card__status--closed'">
        {{ item.is_open ? t('announcementCard.open') : t('announcementCard.closed') }}
      </span>
      <img v-if="item.photo" :src="item.photo" :alt="item.title" loading="lazy" />
      <svg v-else class="announcement-card__thumb-icon" viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <path d="M24 4 L40 10 V22 Q40 36 24 44 Q8 36 8 22 V10 Z" fill="currentColor" opacity="0.16" />
        <path d="M24 4 L40 10 V22 Q40 36 24 44 Q8 36 8 22 V10 Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
        <path d="M16 23 L21 29 L33 15" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </div>
    <div class="announcement-card__body">
      <time class="announcement-card__date" :class="{ 'announcement-card__date--empty': !item.date }" :datetime="item.date || undefined">{{ item.date ? formatDate(item.date) : ' ' }}</time>
      <h3 class="announcement-card__title">{{ item.title }}</h3>
      <p class="announcement-card__excerpt">
        <template v-for="(part, i) in excerptParts" :key="i">
          <a v-if="part.isLink" :href="item.link" target="_blank" rel="noopener" class="announcement-card__inline-link" @click.stop>{{ part.text }}</a>
          <template v-else>{{ part.text }}</template>
        </template>
      </p>
    </div>
  </article>
</template>

<style scoped>
.announcement-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  text-align: left;
  transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}

.announcement-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.announcement-card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.announcement-card--featured {
  flex-direction: row;
}

.announcement-card--featured .announcement-card__thumb {
  width: 42%;
  aspect-ratio: auto;
  flex-shrink: 0;
}

.announcement-card--featured .announcement-card__body {
  min-width: 0;
  padding: var(--space-5);
  justify-content: center;
}

.announcement-card--featured .announcement-card__title {
  font-size: 1.4rem;
  line-height: 1.3;
}

.announcement-card--featured .announcement-card__excerpt {
  font-size: 1rem;
  -webkit-line-clamp: 4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 700px) {
  .announcement-card--featured {
    flex-direction: column;
  }

  .announcement-card--featured .announcement-card__thumb {
    width: 100%;
    aspect-ratio: 16 / 9;
  }
}

.announcement-card__thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  flex: none;
  width: 100%;
  min-height: 0;
  overflow: hidden;
  background: var(--color-primary-light);
}

.announcement-card__status {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1;
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

.announcement-card__status--open {
  background: rgba(66, 183, 88, 0.92);
  color: #fff;
}

.announcement-card__status--closed {
  background: rgba(23, 33, 28, 0.55);
  color: #fff;
}

.announcement-card__thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.announcement-card__thumb--empty {
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-bg-alt));
  display: flex;
  align-items: center;
  justify-content: center;
}

.announcement-card__thumb-icon {
  width: 56px;
  height: 56px;
  color: var(--color-primary);
  opacity: 0.55;
}

.announcement-card__body {
  flex: 1;
  min-height: 0;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.announcement-card__date {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.announcement-card__date--empty {
  visibility: hidden;
}

.announcement-card__title {
  color: var(--color-ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announcement-card__excerpt {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announcement-card__inline-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.announcement-card__inline-link:hover {
  color: var(--color-primary-dark);
}
</style>
