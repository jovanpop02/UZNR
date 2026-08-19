<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import FeatureGrid from '../components/FeatureGrid.vue'
import SafetyIllustration from '../components/SafetyIllustration.vue'
import { isIOS } from '../platform'

const { t } = useI18n()

const dokumentaDocs = [
  {
    title: 'Odluka o osnivanju UZNRCG',
    icon: 'seal',
    file: '/documents/Odluka-o-osnivanju-UZNR-Crne-Gore.pdf',
    sizeKb: 176,
    description: 'Zvanična odluka osnivačke skupštine, donesena u Podgorici 04.02.2000. godine, na osnovu čl. 10 i čl. 11 Zakona o nevladinim organizacijama ("Sl. list RCG", br. 27/99).',
  },
  {
    title: 'Program UZNRCG',
    icon: 'compass',
    file: '/documents/biblioteka/dokumenta-program.pdf',
    sizeKb: 175,
    description: 'Program rada Udruženja — ciljevi, prioriteti i planirane aktivnosti na unapređenju zaštite i zdravlja na radu.',
  },
  {
    title: 'Statut UZNRCG',
    icon: 'book',
    file: '/documents/biblioteka/dokumenta-statut.pdf',
    sizeKb: 55,
    description: 'Osnovni akt Udruženja kojim se uređuju ciljevi, djelatnost, organi i način rada.',
  },
]

const previewDoc = ref(null)

function openPreview(doc) {
  if (isIOS()) {
    window.open(doc.file, '_blank', 'noopener')
    return
  }
  previewDoc.value = doc
}

function closePreview() {
  previewDoc.value = null
}

function formatSize(sizeKb) {
  if (sizeKb >= 1024) return `${(sizeKb / 1024).toFixed(1)} MB`
  return `${sizeKb} KB`
}
</script>

<template>
  <div>
  <section class="section onama-intro">
    <div class="container onama-intro__inner">
      <div class="onama-intro__text-col">
        <h1>{{ t('about.title') }}</h1>
        <p class="onama-intro__text">
          {{ t('about.intro') }}
        </p>
      </div>
      <SafetyIllustration variant="mission" class="onama-intro__illustration" />
    </div>
  </section>

  <FeatureGrid />

  <section class="section section--alt onama-story">
    <div class="container onama-story__inner">
      <h2>{{ t('about.storyTitle') }}</h2>

      <p>
        Na osnovu čl. 10 i čl. 11 Zakona o nevladinim organizacijama
        („Sl. list RCG“, br. 27/99), osnivači Udruženja zaštite na radu Crne
        Gore su na sjednici osnivačke skupštine u Podgorici, dana
        04.02.2000. godine, donijeli Odluku o osnivanju Udruženja zaštite
        na radu Crne Gore.
      </p>

      <p>
        Za kratko vrijeme svog postojanja Udruženje je okupilo značajan broj
        članova iz svih sektora privredne djelatnosti, koji zapošljavaju
        preko 30.000 radnika. Ciljevi Udruženja i aktivnosti koje vodi radi
        njihovog postizanja čine da Udruženje iz dana u dan postaje sve
        brojnije i sve moćnije, što opravdava njegovo formiranje i garantuje
        da će u bliskoj budućnosti postati značajan faktor u privredi i
        društvu Crne Gore.
      </p>

      <p>
        Naše Udruženje je otvoreno za povezivanje sa sličnim organizacijama
        koje se bave zaštitom i zdravljem na radu ili čiji je interes
        unapređenje ove veoma značajne oblasti.
      </p>
    </div>
  </section>

  <section id="dokumenta" class="section section--alt onama-document">
    <div class="container">
      <p class="section-label">{{ t('about.documentsLabel') }}</p>
      <h2 class="section-title">{{ t('about.documentsTitle') }}</h2>
      <p class="onama-document__lead">
        {{ t('about.documentsLead') }}
      </p>

      <div class="doc-grid">
        <article v-for="doc in dokumentaDocs" :key="doc.file" class="official-doc">
          <span class="official-doc__badge" aria-hidden="true">
            <svg v-if="doc.icon === 'seal'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="12" cy="9" r="6" />
              <path d="m8.5 9 2.2 2.2L15.5 6.5" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M9 14.5 7 22l5-2.5 5 2.5-2-7.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-else-if="doc.icon === 'compass'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="12" cy="12" r="9" />
              <path d="m15 9-4.5 1.5L9 15l4.5-1.5L15 9Z" stroke-linejoin="round" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M4 5.5C4 4.67 4.67 4 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5v-13Z" stroke-linejoin="round" />
              <path d="M20 5.5c0-.83-.67-1.5-1.5-1.5H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5v-13Z" stroke-linejoin="round" />
            </svg>
          </span>

          <h3 class="official-doc__title">{{ doc.title }}</h3>
          <p class="official-doc__desc">{{ doc.description }}</p>

          <div class="official-doc__footer">
            <span class="official-doc__size">PDF · {{ formatSize(doc.sizeKb) }}</span>
            <div class="official-doc__actions">
              <button type="button" class="btn btn--ghost official-doc__btn" @click="openPreview(doc)">{{ t('about.preview') }}</button>
              <a class="btn btn--primary official-doc__btn" :href="doc.file" target="_blank" rel="noopener" download>{{ t('about.download') }}</a>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>

  <div v-if="previewDoc" class="preview-overlay" @click.self="closePreview">
    <div class="preview-modal">
      <div class="preview-modal__header">
        <div class="preview-modal__title-col">
          <h3>{{ previewDoc.title }}</h3>
          <p>{{ formatSize(previewDoc.sizeKb) }}</p>
        </div>
        <div class="preview-modal__actions">
          <a class="btn btn--primary" :href="previewDoc.file" target="_blank" rel="noopener" download>{{ t('about.download') }}</a>
          <button type="button" class="icon-btn preview-modal__close" :title="t('about.close')" @click="closePreview">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
            </svg>
          </button>
        </div>
      </div>
      <embed :src="previewDoc.file" type="application/pdf" class="preview-modal__frame" />
    </div>
  </div>

  <section class="section section--alt onama-values">
    <div class="container onama-values__grid">
      <div class="values-col">
        <h2>{{ t('about.valuesTitle1') }}</h2>
        <p>
          S obzirom na navedene činjenice, jasno je da je Udruženje zaštite na
          radu Crne Gore udruženje sa snažnim glasom poslodavaca, preduzetnika
          i svih zaposlenih u Crnoj Gori, u koje je dobrodošao svaki novi član
          i koje poziva na saradnju sve one koji rade u interesu oporavka
          crnogorske privrede, uspješnog procesa tranzicije, stvaranja
          slobodnog tržišta i ulaska Crne Gore u evropske i međunarodne
          integracije, u kojima oblast zaštite i zdravlja na radu ima snažno
          prisustvo.
        </p>
        <p>
          Udruženje zaštite na radu je nevladina i nestranačka organizacija
          čiji članovi i organi djeluju u skladu sa Statutom i koja svojim
          ukupnim i pojedinačnim djelovanjem promoviše poštovanje svih normi
          zaštite i zdravlja na radu u savremenoj privredi i društvu. Članovi
          plaćaju članarinu po utvrđenom iznosu.
        </p>
      </div>
      <div class="values-col">
        <h2>{{ t('about.valuesTitle2') }}</h2>
        <p>
          Udruženje zaštite na radu Crne Gore omogućava svojim članovima punu
          slobodu angažovanja i u potpunosti podržava aktivnosti svojih
          članova u okviru drugih organizacija i udruženja čiji je interes
          unapređenje sistema zaštite i zdravlja na radu.
        </p>
        <p>
          Udruženje i njegovi članovi čine sve da obezbijede zdravlje i
          sigurnost zaposlenih, kao uslov normalnog poslovanja. Svaki član
          udruženja je obavezan da uskladi svoje poslovanje sa stručnim,
          sigurnosnim i zdravstvenim propisima i standardima.
        </p>
        <p>
          Aktivnosti Udruženja, njegovih organa i tijela ne mogu se koristiti
          za promociju i ostvarivanje pojedinačnih ili grupnih interesa
          njegovih članova koji nisu u skladu sa njegovim Statutom. Bilo
          kakav pokušaj zloupotrebe udruženja, njegovog imena i njegovih
          aktivnosti u političke, ekonomske, socijalne ili bilo koje druge
          svrhe, Upravni odbor udruženja sankcionisaće shodno ovlašćenjima
          koja su mu data.
        </p>
      </div>
    </div>
  </section>
  </div>
</template>

<style scoped>
.onama-intro {
  padding-bottom: var(--space-5);
}

.onama-intro__inner {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  max-width: 960px;
}

.onama-intro__text-col {
  flex: 1;
  min-width: 0;
  max-width: 480px;
}

.onama-intro__text {
  color: var(--color-text);
  font-size: 1.05rem;
  margin-top: var(--space-3);
}

.onama-intro__illustration {
  width: 260px;
  flex-shrink: 0;
}

.onama-story__inner {
  max-width: 760px;
  margin-inline: auto;
  text-align: center;
}

.onama-story__inner h2 {
  margin-bottom: var(--space-4);
}

.onama-story__inner p {
  color: var(--color-text);
  text-align: left;
}

.onama-story__inner p + p {
  margin-top: var(--space-3);
}

.onama-values__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.onama-values__grid h2 {
  margin-bottom: var(--space-3);
}

.onama-values__grid p + p {
  margin-top: var(--space-3);
}

.onama-values__grid p {
  color: var(--color-text);
}

.onama-document__lead {
  color: var(--color-text-muted);
  font-size: 1.02rem;
  max-width: 620px;
  margin-top: calc(var(--space-2) * -1);
  margin-bottom: var(--space-5);
}

.doc-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.official-doc {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  padding-top: calc(var(--space-5) + 3px);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.official-doc:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.official-doc::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-dark));
}

.official-doc__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  margin-bottom: var(--space-4);
}

.official-doc__badge svg {
  width: 26px;
  height: 26px;
}

.official-doc__title {
  font-size: 1.05rem;
  margin-bottom: 8px;
}

.official-doc__desc {
  color: var(--color-text-muted);
  font-size: 0.88rem;
  flex: 1;
  margin-bottom: var(--space-4);
}

.official-doc__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  flex-wrap: wrap;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.official-doc__size {
  color: var(--color-text-muted);
  font-size: 0.78rem;
  white-space: nowrap;
}

.official-doc__actions {
  display: flex;
  gap: 8px;
}

.official-doc__btn {
  padding: 8px 16px;
  font-size: 0.85rem;
}

.btn--ghost {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-ink);
}

.btn--ghost:hover {
  background: var(--color-bg-alt);
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.icon-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(23, 33, 28, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  z-index: 100;
}

.preview-modal {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
}

.preview-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.preview-modal__title-col h3 {
  font-size: 1rem;
  margin-bottom: 2px;
}

.preview-modal__title-col p {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.preview-modal__actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-modal__frame {
  flex: 1;
  width: 100%;
  border: none;
}

@media (max-width: 960px) {
  .doc-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 800px) {
  .onama-intro__inner {
    flex-direction: column;
    text-align: center;
  }

  .onama-intro__illustration {
    width: 200px;
    order: -1;
  }

  .onama-values__grid {
    grid-template-columns: 1fr;
  }

  .doc-grid {
    grid-template-columns: 1fr;
  }

  .preview-modal {
    height: 92vh;
  }

  .preview-modal__header {
    flex-direction: column;
    align-items: stretch;
  }

  .preview-modal__actions {
    justify-content: space-between;
  }
}
</style>
