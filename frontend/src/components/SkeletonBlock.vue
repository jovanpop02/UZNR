<script setup>
// Grey placeholders shaped like the content that is loading. Replaces the
// plain "Učitavanje…" line, which read as a stalled page during the backend's
// cold start rather than as work in progress.

defineProps({
  variant: {
    type: String,
    default: 'card',
    validator: (v) => ['card', 'featured', 'row', 'text'].includes(v),
  },
  count: { type: Number, default: 1 },
})
</script>

<template>
  <div class="skeleton" :class="`skeleton--${variant}`" aria-hidden="true">
    <div v-for="n in count" :key="n" class="skeleton__item">
      <div v-if="variant !== 'text'" class="skeleton__media shimmer"></div>
      <div class="skeleton__lines">
        <span class="skeleton__line shimmer"></span>
        <span class="skeleton__line skeleton__line--short shimmer"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton {
  display: grid;
  gap: var(--space-4);
}

.skeleton--card {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.skeleton--row {
  grid-template-columns: 1fr;
}

.skeleton__item {
  display: grid;
  gap: var(--space-3);
}

.skeleton--row .skeleton__item {
  grid-template-columns: 120px 1fr;
  align-items: center;
}

.skeleton__media {
  border-radius: var(--radius-md);
  aspect-ratio: 16 / 10;
  background: var(--color-bg-alt);
}

.skeleton--featured .skeleton__media {
  aspect-ratio: 16 / 7;
}

.skeleton--row .skeleton__media {
  aspect-ratio: 1;
  border-radius: var(--radius-sm);
}

.skeleton__lines {
  display: grid;
  gap: var(--space-2);
}

.skeleton__line {
  display: block;
  height: 12px;
  border-radius: 999px;
  background: var(--color-bg-alt);
}

.skeleton__line--short {
  width: 60%;
}

.shimmer {
  position: relative;
  overflow: hidden;
}

.shimmer::after {
  content: '';
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.65),
    transparent
  );
  animation: skeleton-sweep 1.4s infinite;
}

@keyframes skeleton-sweep {
  100% {
    transform: translateX(100%);
  }
}

/* A looping sweep is exactly the kind of motion this setting asks us to drop. */
@media (prefers-reduced-motion: reduce) {
  .shimmer::after {
    animation: none;
  }
}
</style>
