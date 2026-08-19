<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  title: { type: String, required: true },
  file: { type: String, required: true },
  reference: { type: String, default: '' },
  description: { type: String, default: '' },
  sizeKb: { type: Number, default: null },
  pages: { type: Number, default: null },
  kind: { type: String, default: 'pdf' },
  showKind: { type: Boolean, default: false },
  previewable: { type: Boolean, default: null },
})

const emit = defineEmits(['preview'])

function formatSize(kb) {
  if (kb >= 1024) return `${(kb / 1024).toFixed(1)} MB`
  return `${kb} KB`
}

const canPreview = computed(() => props.previewable ?? props.kind === 'pdf')
</script>

<template>
  <div class="document-card">
    <span class="document-card__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
        <path d="M6 3h9l3 3v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
        <path d="M15 3v3a1 1 0 0 0 1 1h3" />
        <line x1="8" y1="12" x2="16" y2="12" />
        <line x1="8" y1="16" x2="16" y2="16" />
        <line x1="8" y1="8" x2="11" y2="8" />
      </svg>
    </span>
    <div class="document-card__body">
      <h3>{{ title }}</h3>
      <p v-if="reference" class="document-card__reference">{{ reference }}</p>
      <p v-if="description" class="document-card__text">{{ description }}</p>
      <p class="document-card__meta">
        <template v-if="pages">{{ pages }} {{ t('documentCard.pagesUnit') }} · </template>
        <template v-if="showKind">{{ kind.toUpperCase() }}<template v-if="sizeKb"> · </template></template>
        <template v-if="sizeKb">{{ formatSize(sizeKb) }}</template>
      </p>
    </div>
    <div class="document-card__actions">
      <button v-if="canPreview" type="button" class="btn btn--ghost" @click="emit('preview')">{{ t('documentCard.preview') }}</button>
      <a class="btn btn--primary" :href="file" target="_blank" rel="noopener" download>{{ t('documentCard.download') }}</a>
    </div>
  </div>
</template>

<style scoped>
.document-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.document-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.document-card__icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.document-card__icon svg {
  width: 24px;
  height: 24px;
}

.document-card__body {
  flex: 1;
  min-width: 0;
}

.document-card__body h3 {
  font-size: 1rem;
  margin-bottom: 2px;
}

.document-card__reference {
  color: var(--color-text-muted);
  font-size: 0.88rem;
  margin-bottom: 2px;
}

.document-card__text {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.document-card__meta {
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.document-card__actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

.btn--ghost {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-ink);
}

.btn--ghost:hover {
  background: var(--color-bg-alt);
}

@media (max-width: 560px) {
  .document-card {
    flex-wrap: wrap;
  }

  .document-card__actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
