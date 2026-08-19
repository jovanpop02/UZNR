<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchMembers } from '../api'
import MemberCard from './MemberCard.vue'
import SkeletonBlock from './SkeletonBlock.vue'
import WakingNotice from './WakingNotice.vue'

const { t } = useI18n()
const members = ref([])
const loading = ref(true)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    members.value = await fetchMembers()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="section section--alt members">
    <div class="container">
      <h2 v-reveal class="section-title">{{ t('membersSection.title') }}</h2>
      <template v-if="loading">
        <SkeletonBlock variant="card" :count="6" />
        <WakingNotice />
      </template>
      <div v-else-if="error" class="members__error">
        <p class="state-message state-message--error">{{ t('membersSection.error') }}</p>
        <button type="button" class="btn btn--primary" @click="load">{{ t('common.retry') }}</button>
      </div>
      <p v-else-if="!members.length" class="state-message">{{ t('membersSection.empty') }}</p>
      <div v-else v-reveal="1" class="members__grid">
        <MemberCard v-for="member in members" :key="member.name" :member="member" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.members__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-3);
}

.members__grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-3);
}

@media (max-width: 1024px) {
  .members__grid {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    margin-inline: calc(var(--space-4) * -1);
    padding-inline: var(--space-4);
    padding-bottom: var(--space-2);
  }

  .members__grid > * {
    flex: 0 0 128px;
    scroll-snap-align: start;
  }
}

@media (max-width: 600px) {
  .members {
    padding-block: var(--space-5);
  }

  .members .section-title {
    margin-bottom: var(--space-4);
  }

  .members__grid {
    gap: var(--space-2);
  }

  .members__grid > * {
    flex-basis: 108px;
  }
}
</style>
