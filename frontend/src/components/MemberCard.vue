<script setup>
defineProps({
  member: { type: Object, required: true },
})

function initials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}
</script>

<template>
  <a class="member-card" :href="member.url" target="_blank" rel="noopener noreferrer">
    <img v-if="member.logo" class="member-card__logo" :src="member.logo" :alt="member.name" loading="lazy" />
    <span v-else class="member-card__mark">{{ initials(member.name) }}</span>
  </a>
</template>

<style scoped>
.member-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 96px;
  padding: var(--space-3);
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}

.member-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.member-card__logo {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.member-card__mark {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-primary);
}
</style>
