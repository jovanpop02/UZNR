<script setup>
import HeroSection from '../components/HeroSection.vue'
import NewsSection from '../components/NewsSection.vue'
import MembersSection from '../components/MembersSection.vue'
import ImportantLinksSection from '../components/ImportantLinksSection.vue'
</script>

<template>
  <div>
    <HeroSection />
    <section class="section news-row">
      <div class="news-row__container news-row__grid">
        <NewsSection />
        <ImportantLinksSection />
      </div>
    </section>
    <MembersSection />
  </div>
</template>

<style scoped>
.news-row__container {
  width: 100%;
  max-width: 1440px;
  margin-inline: auto;
  padding-inline: var(--space-4);
}

.news-row__grid {
  display: grid;
  grid-template-columns: 2.6fr 1fr;
  gap: var(--space-6);
  align-items: start;
}

.news-row__grid > * {
  min-width: 0;
}

@media (max-width: 900px) {
  .news-row__grid {
    grid-template-columns: 1fr;
    gap: var(--space-5);
  }
}

@media (max-width: 600px) {
  .news-row {
    padding-block: var(--space-5);
  }
}
</style>
