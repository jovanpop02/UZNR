<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { isPageLoading } from '../loading'

const { t } = useI18n()
const showBar = ref(false)
const showBadge = ref(false)
let barTimer = null
let badgeTimer = null

watch(isPageLoading, (loading) => {
  clearTimeout(barTimer)
  clearTimeout(badgeTimer)
  if (loading) {
    barTimer = setTimeout(() => {
      showBar.value = true
    }, 120)
    badgeTimer = setTimeout(() => {
      showBadge.value = true
    }, 180)
  } else {
    showBar.value = false
    showBadge.value = false
  }
})
</script>

<template>
  <Transition name="page-loader-fade">
    <div v-if="isPageLoading && showBar" class="page-loader-bar" aria-hidden="true">
      <div class="page-loader-bar__sweep"></div>
    </div>
  </Transition>

  <Transition name="page-loader-badge-fade">
    <div v-if="isPageLoading && showBadge" class="page-loader-badge" role="status" :aria-label="t('loader.pageLoading')">
      <span class="page-loader-badge__ring"></span>
      <svg class="page-loader-badge__shield" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 2 L20 5 V11 Q20 18 12 22 Q4 18 4 11 V5 Z" fill="var(--color-primary)" />
        <path class="page-loader-badge__check" d="M7.5 12 L10.5 15 L16.5 8.5" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none" />
      </svg>
    </div>
  </Transition>
</template>

<style scoped>
.page-loader-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 999;
  overflow: hidden;
  background: var(--color-primary-light);
}

.page-loader-bar__sweep {
  height: 100%;
  width: 100%;
  background: linear-gradient(90deg, transparent 0%, var(--color-primary) 35%, var(--color-accent-dark, var(--color-primary)) 50%, var(--color-primary) 65%, transparent 100%);
  background-size: 60% 100%;
  animation: page-loader-sweep 1.1s ease-in-out infinite;
}

@keyframes page-loader-sweep {
  0% {
    transform: translateX(-120%);
  }
  100% {
    transform: translateX(220%);
  }
}

.page-loader-fade-enter-active {
  transition: opacity 0.15s ease;
}

.page-loader-fade-leave-active {
  transition: opacity 0.25s ease 0.1s;
}

.page-loader-fade-enter-from,
.page-loader-fade-leave-to {
  opacity: 0;
}

.page-loader-badge {
  position: fixed;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 998;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-loader-badge__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(66, 183, 88, 0.35);
  animation: page-loader-pulse 1.4s ease-out infinite;
}

@keyframes page-loader-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(66, 183, 88, 0.35);
  }
  100% {
    box-shadow: 0 0 0 12px rgba(66, 183, 88, 0);
  }
}

.page-loader-badge__shield {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 6px rgba(23, 33, 28, 0.25));
}

.page-loader-badge__check {
  stroke-dasharray: 14;
  stroke-dashoffset: 14;
  animation: page-loader-check 1.2s ease-in-out infinite;
}

@keyframes page-loader-check {
  0% {
    stroke-dashoffset: 14;
  }
  40% {
    stroke-dashoffset: 0;
  }
  70% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -14;
  }
}

.page-loader-badge-fade-enter-active,
.page-loader-badge-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-loader-badge-fade-enter-from,
.page-loader-badge-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.7);
}

@media (prefers-reduced-motion: reduce) {
  .page-loader-bar__sweep,
  .page-loader-badge__ring,
  .page-loader-badge__check {
    animation: none;
  }
}
</style>
