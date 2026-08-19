<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { faqs as bundledFaqs } from '../data/pitanja'
import { text, usePageSections, withFallback } from '../cms'
import questionsIllustration from '../assets/illustrations/questions.svg'

const { t, locale } = useI18n()

// Editable under Stranice → Pitanja i odgovori. Answers are stored as plain
// text; a blank line starts a new paragraph and a leading "- " makes a bullet,
// which is what the admin help text tells staff.
const sections = usePageSections('pitanja-odgovori')
const faqs = withFallback(sections, bundledFaqs, (cmsSections) =>
  cmsSections.flatMap((section) =>
    section.items.map((item) => ({
      id: `faq-${item.id}`,
      question: text(item.title, locale.value),
      answer: parseAnswer(text(item.description, locale.value)),
    }))
  )
)

function parseAnswer(body) {
  return body
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean)
    .map((block) =>
      block.startsWith('- ')
        ? { type: 'list', value: block.split('\n').map((line) => line.replace(/^-\s*/, '')) }
        : { type: 'text', value: block }
    )
}

const searchText = ref('')
// Start with the first answer open so the page never reads as a wall of
// closed rows — visitors can see what an answer looks like before clicking.
const openIds = ref(new Set())

// Which entry is first depends on the admin's ordering, so the default-open row
// is resolved from the current list rather than captured once at setup.
function isFirst(id) {
  return faqs.value[0]?.id === id
}

const filtered = computed(() => {
  const q = searchText.value.trim().toLowerCase()
  if (!q) return faqs.value
  return faqs.value.filter((faq) => {
    if (faq.question.toLowerCase().includes(q)) return true
    return faq.answer.some((block) =>
      block.type === 'list'
        ? block.value.some((item) => item.toLowerCase().includes(q))
        : block.value.toLowerCase().includes(q)
    )
  })
})

function isOpen(id) {
  // While searching, show every match expanded — hunting through collapsed
  // rows for the term you just typed defeats the point of the search.
  if (searchText.value.trim()) return true
  if (openIds.value.has(id)) return true
  return isFirst(id) && !closedIds.value.has(id)
}

// Tracked separately from openIds so the first row, which starts open without
// ever being clicked, can also be closed by clicking it.
const closedIds = ref(new Set())

function toggle(id) {
  if (searchText.value.trim()) return
  const open = new Set(openIds.value)
  const closed = new Set(closedIds.value)
  if (isOpen(id)) {
    open.delete(id)
    closed.add(id)
  } else {
    open.add(id)
    closed.delete(id)
  }
  openIds.value = open
  closedIds.value = closed
}
</script>

<template>
  <section class="section qa">
    <div class="container">
      <header class="qa__head">
        <h1>{{ t('qa.title') }}</h1>
        <p class="qa__lead">{{ t('qa.lead') }}</p>
      </header>

      <div class="qa__search">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="M20 20l-3.5-3.5" stroke-linecap="round" />
        </svg>
        <input v-model="searchText" type="search" :placeholder="t('qa.searchPlaceholder')" :aria-label="t('qa.searchPlaceholder')" />
      </div>

      <p v-if="!filtered.length" class="state-message">{{ t('qa.noResults') }}</p>

      <ul v-else class="qa__list">
        <li v-for="(faq, i) in filtered" :key="faq.id" v-reveal="i % 3" class="qa__item" :class="{ 'qa__item--open': isOpen(faq.id) }">
          <h2 class="qa__question-wrap">
            <button
              type="button"
              class="qa__question"
              :aria-expanded="isOpen(faq.id)"
              :aria-controls="`answer-${faq.id}`"
              @click="toggle(faq.id)"
            >
              <span class="qa__number">{{ String(i + 1).padStart(2, '0') }}</span>
              <span class="qa__question-text">{{ faq.question }}</span>
              <svg class="qa__chevron" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </h2>

          <div v-show="isOpen(faq.id)" :id="`answer-${faq.id}`" class="qa__answer">
            <template v-for="(block, bi) in faq.answer" :key="bi">
              <p v-if="block.type === 'text'" class="qa__paragraph">{{ block.value }}</p>
              <ul v-else class="qa__bullets">
                <li v-for="(item, ii) in block.value" :key="ii">{{ item }}</li>
              </ul>
            </template>
          </div>
        </li>
      </ul>

      <aside class="qa__cta">
        <img
          class="qa__cta-illustration"
          :src="questionsIllustration"
          alt=""
          aria-hidden="true"
          loading="lazy"
        />
        <div class="qa__cta-copy">
          <h2 class="qa__cta-title">{{ t('qa.ctaTitle') }}</h2>
          <p class="qa__cta-text">{{ t('qa.ctaText') }}</p>
        </div>
        <router-link class="btn btn--primary" to="/kontakt">{{ t('qa.askBtn') }}</router-link>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.qa__head {
  max-width: 720px;
}

.qa__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  margin-top: var(--space-3);
}

.qa__search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  max-width: 420px;
  margin-top: var(--space-5);
  padding: 10px var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-card-bg);
  color: var(--color-text-muted);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.qa__search:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.qa__search input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  font: inherit;
  font-size: 0.95rem;
  color: var(--color-ink);
}

.qa__list {
  list-style: none;
  margin: var(--space-5) 0 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.qa__item {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-card-bg);
  overflow: hidden;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.qa__item--open {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.qa__question-wrap {
  margin: 0;
  font-size: inherit;
  font-weight: inherit;
}

.qa__question {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 0;
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
  color: var(--color-ink);
}

.qa__question:hover .qa__question-text {
  color: var(--color-primary-dark);
}

.qa__number {
  flex: 0 0 auto;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--color-primary);
  padding-top: 3px;
  font-variant-numeric: tabular-nums;
}

.qa__question-text {
  flex: 1;
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.4;
  transition: color 0.15s ease;
}

.qa__chevron {
  flex: 0 0 auto;
  color: var(--color-text-muted);
  transition: transform 0.2s ease, color 0.15s ease;
}

.qa__item--open .qa__chevron {
  transform: rotate(180deg);
  color: var(--color-primary);
}

.qa__answer {
  padding: 0 var(--space-4) var(--space-4);
  /* Align the answer with the question text, past the number gutter. */
  padding-left: calc(var(--space-4) + 24px + var(--space-3));
  display: grid;
  gap: var(--space-3);
}

.qa__paragraph {
  color: var(--color-text);
}

.qa__bullets {
  margin: 0;
  padding-left: var(--space-4);
  display: grid;
  gap: var(--space-2);
  color: var(--color-text);
}

.qa__bullets li::marker {
  color: var(--color-primary);
}

.qa__cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-top: var(--space-6);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
}

.qa__cta-copy {
  flex: 1;
  min-width: 220px;
}

.qa__cta-illustration {
  flex-shrink: 0;
  width: 132px;
  height: auto;
}

@media (max-width: 640px) {
  .qa__cta-illustration {
    display: none;
  }
}

.qa__cta-title {
  font-size: 1.15rem;
}

.qa__cta-text {
  color: var(--color-text-muted);
  margin-top: var(--space-1);
  max-width: 46ch;
}

@media (max-width: 600px) {
  .qa__question {
    padding: var(--space-3);
    gap: var(--space-2);
  }

  .qa__answer {
    padding: 0 var(--space-3) var(--space-3);
    padding-left: var(--space-3);
  }

  .qa__cta {
    padding: var(--space-4);
  }
}
</style>
