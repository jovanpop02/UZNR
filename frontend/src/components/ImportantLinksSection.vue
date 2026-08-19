<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchImportantLinks } from '../api'
import { localizeList } from '../cms'
import SkeletonBlock from './SkeletonBlock.vue'

const { t, locale } = useI18n()
const rawLinks = ref([])
const links = computed(() => localizeList(rawLinks.value, locale.value))
const loading = ref(true)

onMounted(async () => {
  try {
    rawLinks.value = await fetchImportantLinks()
  } catch {
    rawLinks.value = []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <aside v-if="loading || links.length" class="important-links">
    <h2 v-reveal class="important-links__title">
      {{ t('importantLinks.title') }}
      <span class="important-links__title-mark"></span>
    </h2>
    <p v-reveal="1" class="important-links__intro">{{ t('importantLinks.intro') }}</p>

    <SkeletonBlock v-if="loading" variant="row" :count="4" />

    <ul v-else-if="links.length" v-reveal="2" class="important-links__list">
      <li v-for="link in links" :key="link.title">
        <a
          class="important-links__item"
          :href="link.href"
          target="_blank"
          rel="noopener"
          :download="link.is_file ? true : null"
        >
          <span class="important-links__logo">
            <img v-if="link.logo" :src="link.logo" :alt="link.title" />
            <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M10 14a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 5.5" stroke-linecap="round" />
              <path d="M14 10a5 5 0 0 0-7.07 0L4.1 12.83a5 5 0 0 0 7.07 7.07l1.36-1.36" stroke-linecap="round" />
            </svg>
          </span>
          <span class="important-links__name">{{ link.title }}</span>
          <span class="important-links__arrow" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17L17 7M9 7h8v8" stroke-linecap="round" stroke-linejoin="round" /></svg>
          </span>
        </a>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.important-links {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  height: 100%;
  box-shadow: var(--shadow-sm);
}

.important-links__title {
  display: inline-block;
  font-size: 1.3rem;
  margin-bottom: var(--space-2);
  position: relative;
}

.important-links__title-mark {
  display: block;
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-accent-dark);
  margin-top: 10px;
}

.important-links__intro {
  font-size: 0.86rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: var(--space-4);
}

.important-links__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.important-links__item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  text-decoration: none;
  color: var(--color-ink);
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}

.important-links__item:hover {
  background: var(--color-primary-light);
  border-color: var(--color-border);
  transform: translateX(2px);
}

.important-links__logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #fff;
  border: 1px solid var(--color-border);
  color: var(--color-accent-dark);
  overflow: hidden;
}

.important-links__logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 8px;
}

.important-links__name {
  flex: 1;
  min-width: 0;
  font-weight: 600;
  font-size: 0.95rem;
  line-height: 1.35;
}

.important-links__arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  transition: background 0.15s ease, color 0.15s ease;
}

.important-links__item:hover .important-links__arrow {
  background: var(--color-primary);
  color: #fff;
}

@media (max-width: 480px) {
  .important-links {
    padding: var(--space-4);
  }

  .important-links__item {
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
  }

  .important-links__logo {
    width: 40px;
    height: 40px;
  }

  .important-links__logo img {
    padding: 6px;
  }

  .important-links__name {
    font-size: 0.88rem;
  }

  .important-links__arrow {
    width: 24px;
    height: 24px;
  }
}
</style>
