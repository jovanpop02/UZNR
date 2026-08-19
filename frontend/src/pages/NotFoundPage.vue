<script setup>
import { useI18n } from 'vue-i18n'
import notFoundIllustration from '../assets/illustrations/not-found.svg'

const { t } = useI18n()
</script>

<template>
  <section class="section notfound">
    <div class="container notfound__inner">
      <img
        class="notfound__illustration"
        :src="notFoundIllustration"
        alt=""
        aria-hidden="true"
      />
      <p class="section-label">{{ t('notFound.label') }}</p>
      <h1 class="notfound__title">{{ t('notFound.title') }}</h1>
      <p class="notfound__text">{{ t('notFound.text') }}</p>
      <div class="notfound__actions">
        <router-link class="btn btn--primary" to="/">{{ t('notFound.backHome') }}</router-link>
        <router-link class="btn btn--ghost" to="/arhiva">{{ t('notFound.searchArchive') }}</router-link>
      </div>
    </div>
  </section>
</template>

<style scoped>
.notfound {
  min-height: 60vh;
  display: flex;
  align-items: center;
}

.notfound__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 560px;
}

.notfound__illustration {
  width: min(320px, 70vw);
  height: auto;
  margin-bottom: var(--space-4);
}

.notfound__title {
  margin-bottom: var(--space-3);
}

.notfound__text {
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.notfound__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-3);
}

.btn--ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-ink);
}

.btn--ghost:hover {
  background: var(--color-bg-alt);
}
</style>
