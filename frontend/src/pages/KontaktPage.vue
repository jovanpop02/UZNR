<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ContactForm from '../components/ContactForm.vue'
import contactIllustration from '../assets/illustrations/contact.svg'

const { t } = useI18n()

const contactCards = computed(() => [
  {
    title: t('contact.addressTitle'),
    icon: 'pin',
    lines: ['4. jul 109/3', '81000 Podgorica', 'Crna Gora'],
  },
  {
    title: t('contact.phoneEmailTitle'),
    icon: 'mail',
    links: [
      { text: 'info@uznr.me', href: 'mailto:info@uznr.me' },
      { text: '+382 67 412 900', href: 'tel:+38267412900' },
      { text: '+382 20 671 340', href: 'tel:+38220671340' },
    ],
  },
  {
    title: t('contact.hoursTitle'),
    icon: 'clock',
    lines: [t('contact.hoursLine1'), t('contact.hoursLine2')],
  },
])

const socials = [
  { label: 'Facebook', href: 'https://www.facebook.com/uznr.me', icon: 'facebook' },
  { label: 'Instagram', href: 'https://www.instagram.com/uznr.me/', icon: 'instagram' },
  { label: 'YouTube', href: 'https://www.youtube.com/@udruzenjezastitenaraducrne2151', icon: 'youtube' },
]
</script>

<template>
  <div>
  <section class="section kontakt-hero">
    <div class="container kontakt-hero__inner">
      <div class="kontakt-hero__text">
        <h1>{{ t('contact.title') }}</h1>
        <p class="kontakt-hero__lead">
          {{ t('contact.lead') }}
        </p>
      </div>
      <img
        class="kontakt-hero__illustration"
        :src="contactIllustration"
        alt=""
        aria-hidden="true"
      />
    </div>
  </section>

  <section class="section section--alt kontakt-cards">
    <div class="container kontakt-cards__grid">
      <div v-for="card in contactCards" :key="card.title" class="kontakt-card">
        <span class="kontakt-card__icon" aria-hidden="true">
          <svg v-if="card.icon === 'pin'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M12 21s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12Z" stroke-linejoin="round" />
            <circle cx="12" cy="9" r="2.6" />
          </svg>
          <svg v-else-if="card.icon === 'mail'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <rect x="3" y="5" width="18" height="14" rx="2.5" />
            <path d="m4 7 8 6 8-6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v5l3.5 2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </span>
        <h3>{{ card.title }}</h3>
        <p v-if="card.lines">
          <template v-for="(line, i) in card.lines" :key="i">{{ line }}<br v-if="i < card.lines.length - 1" /></template>
        </p>
        <p v-else class="kontakt-card__links">
          <a v-for="link in card.links" :key="link.href" :href="link.href">{{ link.text }}</a>
        </p>
      </div>
    </div>
  </section>

  <section class="section kontakt-form">
    <div class="container">
      <header class="kontakt-form__head">
        <p class="section-label">{{ t('contact.form.label') }}</p>
        <h2>{{ t('contact.form.title') }}</h2>
        <p class="kontakt-form__lead">{{ t('contact.form.lead') }}</p>
      </header>
      <ContactForm />
    </div>
  </section>

  <section class="section section--alt kontakt-social">
    <div class="container kontakt-social__inner">
      <div>
        <h2>{{ t('contact.followTitle') }}</h2>
        <p class="kontakt-social__text">{{ t('contact.followText') }}</p>
      </div>
      <div class="kontakt-social__links">
        <a v-for="s in socials" :key="s.label" :href="s.href" target="_blank" rel="noopener" class="kontakt-social__link">
          <svg v-if="s.icon === 'facebook'" viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M14 9h3V5h-3c-2.2 0-4 1.8-4 4v2H8v4h2v7h4v-7h3l1-4h-4v-2c0-.6.4-1 1-1z"/></svg>
          <svg v-else-if="s.icon === 'instagram'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><rect x="2" y="6" width="20" height="12" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.5l6 2.5-6 2.5z"/></svg>
          {{ s.label }}
        </a>
      </div>
    </div>
  </section>
  </div>
</template>

<style scoped>
.kontakt-hero__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
}

.kontakt-hero__text {
  min-width: 0;
}

.kontakt-hero__illustration {
  flex-shrink: 0;
  width: min(320px, 34vw);
  height: auto;
}

/* Decoration only -- at narrow widths the heading and lead take the room. */
@media (max-width: 820px) {
  .kontakt-hero__illustration {
    display: none;
  }
}

.kontakt-hero {
  padding-bottom: var(--space-4);
}

.kontakt-hero__lead {
  color: var(--color-text-muted);
  font-size: 1.05rem;
  max-width: 620px;
  margin-top: var(--space-3);
}

.kontakt-cards__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.kontakt-card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.kontakt-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  color: var(--color-primary);
  margin-bottom: var(--space-3);
}

.kontakt-card__icon svg {
  width: 24px;
  height: 24px;
}

.kontakt-card h3 {
  margin-bottom: var(--space-2);
}

.kontakt-card p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
}

.kontakt-card__links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kontakt-card__links a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.kontakt-card__links a:hover {
  text-decoration: underline;
}

.kontakt-form__head {
  max-width: 640px;
  margin-bottom: var(--space-5);
}

.kontakt-form__lead {
  color: var(--color-text-muted);
  margin-top: var(--space-2);
}

.kontakt-social__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.kontakt-social__text {
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.kontakt-social__links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.kontakt-social__link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  color: var(--color-ink);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.kontakt-social__link:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

@media (max-width: 900px) {
  .kontakt-cards__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .kontakt-social__inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
