<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const features = computed(() => [
  {
    title: t('featureGrid.goalsTitle'),
    text: t('featureGrid.goalsText'),
    icon: 'target',
  },
  {
    title: t('featureGrid.visionTitle'),
    text: t('featureGrid.visionText'),
    icon: 'eye',
  },
  {
    title: t('featureGrid.cooperationTitle'),
    text: t('featureGrid.cooperationText'),
    icon: 'cooperation',
  },
  {
    title: t('featureGrid.educationTitle'),
    text: t('featureGrid.educationText'),
    icon: 'book',
  },
])
</script>

<template>
  <section class="section features">
    <div class="container">
      <div class="features__grid">
        <div v-for="(feature, i) in features" :key="feature.title" v-reveal="i">
          <article class="feature-card">
            <span class="feature-card__icon">
              <svg v-if="feature.icon === 'target'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                <circle cx="12" cy="12" r="9" />
                <circle cx="12" cy="12" r="5" />
                <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
              </svg>
              <svg v-else-if="feature.icon === 'eye'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <svg v-else-if="feature.icon === 'cooperation'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                <circle cx="9" cy="12" r="6" />
                <circle cx="15" cy="12" r="6" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
                <path d="M4 5.5C4 4.67 4.67 4 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5v-13Z" />
                <path d="M20 5.5c0-.83-.67-1.5-1.5-1.5H13v16h5.5c.83 0 1.5-.67 1.5-1.5v-13Z" />
              </svg>
            </span>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.text }}</p>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.features__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.feature-card {
  height: 100%;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease;
}

.feature-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.feature-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: var(--space-1);
}

.feature-card__icon svg {
  width: 24px;
  height: 24px;
}

.feature-card p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

@media (max-width: 900px) {
  .features__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .features__grid {
    grid-template-columns: 1fr;
  }
}
</style>
