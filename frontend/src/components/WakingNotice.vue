<script setup>
// Shown only once a request has been outstanding long enough to look broken.
// The backend is on Render's free tier and cold-starts for up to a minute; a
// visitor who isn't told that has no way to tell a waking server from a dead
// site. See src/api.js for where the flag is set.

import { useI18n } from 'vue-i18n'
import { isWakingBackend } from '../api'

const { t } = useI18n()
</script>

<template>
  <p v-if="isWakingBackend" class="waking" role="status">
    <span class="waking__spinner" aria-hidden="true"></span>
    {{ t('common.wakingBackend') }}
  </p>
</template>

<style scoped>
.waking {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding: 10px var(--space-3);
  border-radius: var(--radius-sm);
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 0.88rem;
  font-weight: 600;
}

.waking__spinner {
  flex: 0 0 auto;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: waking-spin 0.8s linear infinite;
}

@keyframes waking-spin {
  100% {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .waking__spinner {
    animation-duration: 2.4s;
  }
}
</style>
