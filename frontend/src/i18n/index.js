import { createI18n } from 'vue-i18n'
import mne from './locales/mne.js'
import en from './locales/en.js'
import componentsMne from './locales/sections/components.mne.js'
import componentsEn from './locales/sections/components.en.js'
import pagesMne from './locales/sections/pages.mne.js'
import pagesEn from './locales/sections/pages.en.js'

const mergedMne = { ...mne, ...componentsMne, ...pagesMne }
const mergedEn = { ...en, ...componentsEn, ...pagesEn }

const STORAGE_KEY = 'uznr-locale'

function detectLocale() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'mne' || saved === 'en') return saved
  return 'mne'
}

const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'mne',
  messages: { mne: mergedMne, en: mergedEn },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.setAttribute('lang', locale === 'en' ? 'en' : 'sr-Latn-ME')
}

export { STORAGE_KEY }
export default i18n
