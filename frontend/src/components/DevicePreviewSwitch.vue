<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { DEVICES } from '../devicePreview'

const { t } = useI18n()
const open = ref(false)

function openDevice(device) {
  open.value = false
  const left = Math.max(0, Math.round((window.screen.width - device.width) / 2))
  const top = Math.max(0, Math.round((window.screen.height - device.height) / 2))
  window.open(
    window.location.href,
    `uznr-preview-${device.id}`,
    `width=${device.width},height=${device.height},left=${left},top=${top}`
  )
}
</script>

<template>
  <div class="device-switch" :class="{ 'device-switch--open': open }">
    <Transition name="device-switch-panel">
      <div v-if="open" class="device-switch__panel" role="group" :aria-label="t('devicePreview.openWindowGroup')">
        <button
          v-for="device in DEVICES"
          :key="device.id"
          type="button"
          class="device-switch__option"
          @click="openDevice(device)"
        >
          <svg v-if="device.id === 'tablet'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <rect x="4" y="2" width="16" height="20" rx="2.2" />
            <line x1="12" y1="18.3" x2="12.01" y2="18.3" stroke-linecap="round" stroke-width="2.4" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <rect x="7" y="2" width="10" height="20" rx="2.2" />
            <line x1="12" y1="18.3" x2="12.01" y2="18.3" stroke-linecap="round" stroke-width="2.4" />
          </svg>
          {{ device.label }}
          <svg class="device-switch__option-ext" viewBox="0 0 16 16" width="13" height="13" fill="none" aria-hidden="true"><path d="M6 3h7v7M13 3 3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </Transition>

    <button
      type="button"
      class="device-switch__toggle"
      :aria-expanded="open"
      :aria-label="t('devicePreview.compareDevices')"
      @click="open = !open"
    >
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
        <rect x="2.5" y="4" width="13" height="9.5" rx="1.4" />
        <path d="M6 17h5" stroke-linecap="round" />
        <rect x="17" y="9" width="5.5" height="10" rx="1.2" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.device-switch {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 500;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.device-switch__toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  color: var(--color-primary);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}

.device-switch__toggle:hover {
  background: var(--color-primary);
  color: #fff;
  transform: translateY(-1px);
}

.device-switch__panel {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  box-shadow: var(--shadow-md);
}

.device-switch__option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.device-switch__option:hover {
  background: var(--color-bg-alt);
}

.device-switch__option-ext {
  color: var(--color-text-muted);
  margin-left: auto;
}

.device-switch-panel-enter-active,
.device-switch-panel-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
  transform-origin: bottom right;
}

.device-switch-panel-enter-from,
.device-switch-panel-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(6px);
}

@media (max-width: 1024px) {
  .device-switch {
    display: none;
  }
}
</style>
