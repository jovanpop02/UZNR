<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  title: { type: String, required: true },
})

const { t } = useI18n()
</script>

<template>
  <section class="section placeholder">
    <div class="container placeholder__inner">
      <p class="section-label">{{ t('placeholder.label') }}</p>
      <h1>{{ title }}</h1>
      <p class="placeholder__text">{{ t('placeholder.text') }}</p>
      <router-link class="btn btn--primary" to="/">{{ t('placeholder.backHome') }}</router-link>
    </div>
  </section>
</template>

<style scoped>
.placeholder {
  min-height: 50vh;
  display: flex;
  align-items: center;
}

.placeholder__inner {
  max-width: 640px;
}

.placeholder__text {
  color: var(--color-text-muted);
  margin-block: var(--space-3) var(--space-4);
}
</style>
