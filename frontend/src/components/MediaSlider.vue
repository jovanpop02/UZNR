<script setup>
// Horizontal slider shared by the YouTube and Instagram sections so both read
// as the same component. Scroll-snap does the work; the arrows are a
// convenience on top of it, and stay hidden when the track fits on screen or
// when there is no pointer to click them with.

import { onBeforeUnmount, onMounted, ref } from 'vue'

defineProps({
  label: { type: String, default: '' },
  prevLabel: { type: String, required: true },
  nextLabel: { type: String, required: true },
  dark: { type: Boolean, default: false },
})

const track = ref(null)
const atStart = ref(true)
const atEnd = ref(false)
const scrollable = ref(false)

let observer = null

function update() {
  const el = track.value
  if (!el) return
  const max = el.scrollWidth - el.clientWidth
  scrollable.value = max > 4
  atStart.value = el.scrollLeft <= 2
  atEnd.value = el.scrollLeft >= max - 2
}

function page(direction) {
  const el = track.value
  if (!el) return
  const first = el.firstElementChild
  const gap = parseFloat(getComputedStyle(el).columnGap || '16') || 16
  const step = first ? first.getBoundingClientRect().width + gap : el.clientWidth * 0.8
  // Advance by whole cards so a card never lands half-clipped at the edge.
  const perPage = Math.max(1, Math.floor(el.clientWidth / step))
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  el.scrollBy({ left: direction * step * perPage, behavior: reduced ? 'auto' : 'smooth' })
}

onMounted(() => {
  update()
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(update)
    observer.observe(track.value)
  }
  window.addEventListener('resize', update)
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('resize', update)
})

defineExpose({ update })
</script>

<template>
  <div class="slider" :class="{ 'slider--dark': dark }">
    <div class="slider__head">
      <h3 v-if="label" class="slider__label">{{ label }}</h3>
      <div v-show="scrollable" class="slider__nav">
        <button type="button" class="slider__btn" :disabled="atStart" :aria-label="prevLabel" @click="page(-1)">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path d="M15 6l-6 6 6 6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <button type="button" class="slider__btn" :disabled="atEnd" :aria-label="nextLabel" @click="page(1)">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path d="M9 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>
    </div>

    <ul ref="track" class="slider__track" @scroll.passive="update">
      <slot />
    </ul>
  </div>
</template>

<style scoped>
.slider__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  min-height: 38px;
}

.slider__label {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.slider--dark .slider__label {
  color: rgba(255, 255, 255, 0.55);
}

.slider__nav {
  display: flex;
  gap: var(--space-2);
}

.slider__btn {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  cursor: pointer;
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  color: var(--color-ink);
  transition: background 0.15s ease, border-color 0.15s ease, opacity 0.15s ease;
}

.slider__btn:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.slider__btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.slider--dark .slider__btn {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
  color: #fff;
}

.slider--dark .slider__btn:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.slider__track {
  list-style: none;
  margin: 0;
  padding: 0 0 var(--space-3);
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  /* Scrollbar comes from the global rules in style.css — no local override, so
     this strip looks exactly like every other scrollbar on the site. */
}

.slider__track > :deep(*) {
  scroll-snap-align: start;
  flex: 0 0 auto;
}
</style>
