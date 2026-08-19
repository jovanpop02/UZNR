<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import logo from '../assets/uznr-logo.png'
import { setLocale } from '../i18n'
import HeaderSearch from './HeaderSearch.vue'
import HeaderSocial from './HeaderSocial.vue'

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()
const mobileOpen = ref(false)
const mobileSubOpen = reactive({})

// Search and the social links sit in the header bar from tablet up, but fold
// back into the collapsed menu on phones where there isn't room. The language
// toggle stays in the bar at every width. Rendering them in one place or the
// other (rather than duplicating and hiding with CSS) keeps a single copy in
// the accessibility tree.
const PHONE_QUERY = '(max-width: 600px)'
const isPhone = ref(false)
let phoneMq = null

function syncIsPhone(e) {
  isPhone.value = e.matches
}

onMounted(() => {
  phoneMq = window.matchMedia(PHONE_QUERY)
  isPhone.value = phoneMq.matches
  phoneMq.addEventListener('change', syncIsPhone)
})

onBeforeUnmount(() => {
  phoneMq?.removeEventListener('change', syncIsPhone)
})

const localeOptions = [
  { value: 'mne', label: 'ME' },
  { value: 'en', label: 'EN' },
]

const navLinks = computed(() => [
  { label: t('nav.home'), to: '/' },
  { label: t('nav.about'), to: '/o-nama' },
  { label: t('nav.regulations'), to: '/regulativa' },
  { label: t('nav.projects'), to: '/projekti' },
  { label: t('nav.ads'), to: '/oglasi' },
  { label: t('nav.publications'), to: '/publikacije' },
  {
    label: t('nav.library'),
    to: '/biblioteka',
    children: [
      { label: t('nav.libraryExam'), to: '/biblioteka#strucni-ispit' },
      { label: 'EU OSHA', to: '/biblioteka#eu-osha' },
      { label: 'No Time to Lose', to: '/biblioteka#no-time-to-lose' },
    ],
  },
  { label: t('nav.press'), to: '/press' },
  { label: t('nav.qa'), to: '/pitanja-odgovori' },
  { label: t('nav.archive'), to: '/arhiva' },
])

function toggleMobileSub(label) {
  mobileSubOpen[label] = !mobileSubOpen[label]
}

watch(() => route.fullPath, () => {
  mobileOpen.value = false
})

function submitSearch(q) {
  router.push(q ? { path: '/arhiva', query: { q } } : { path: '/arhiva' })
  mobileOpen.value = false
}
</script>

<template>
  <header class="site-header">
    <div class="site-header__inner">
      <router-link class="site-header__brand" to="/">
        <img class="site-header__logo" :src="logo" alt="UZNR – Udruženje zaštite na radu Crne Gore" />
      </router-link>

      <!-- Always in the header bar. From tablet up it also holds search; on
           phones that folds into the menu below. -->
      <div class="site-header__utils">
        <HeaderSearch v-if="!isPhone" @submit="submitSearch" />
        <!-- Segmented control rather than a single toggle: both languages are
             visible and directly selectable, so nobody has to click to find out
             which one they land on. -->
        <div class="lang" role="group" :aria-label="t('header.switchLanguage')">
          <span class="lang__indicator" :class="{ 'lang__indicator--end': locale === 'en' }" aria-hidden="true"></span>
          <button
            v-for="option in localeOptions"
            :key="option.value"
            type="button"
            class="lang__option"
            :class="{ 'lang__option--active': locale === option.value }"
            :aria-pressed="locale === option.value"
            @click="setLocale(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <button
        type="button"
        class="site-header__toggle"
        :aria-expanded="mobileOpen"
        aria-controls="site-header-menu"
        :aria-label="mobileOpen ? t('header.closeMenu') : t('header.openMenu')"
        @click="mobileOpen = !mobileOpen"
      >
        <svg v-if="!mobileOpen" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18" stroke-linecap="round"/></svg>
        <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18" stroke-linecap="round"/></svg>
      </button>

      <div id="site-header-menu" class="site-header__menu" :class="{ 'is-open': mobileOpen }">
        <nav class="site-header__nav" :aria-label="t('header.mainNav')">
          <template v-for="link in navLinks" :key="link.label">
            <div v-if="link.children" class="site-header__nav-item site-header__nav-item--dropdown">
              <div class="site-header__nav-item-row">
                <router-link class="site-header__nav-link" :to="link.to">
                  {{ link.label }}
                </router-link>
                <button
                  type="button"
                  class="site-header__nav-subtoggle"
                  :aria-expanded="!!mobileSubOpen[link.label]"
                  :aria-label="`${t('header.openSubmenu')}: ${link.label}`"
                  @click="toggleMobileSub(link.label)"
                >
                  <svg
                    viewBox="0 0 24 24"
                    width="14"
                    height="14"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    :class="{ 'is-open': mobileSubOpen[link.label] }"
                    aria-hidden="true"
                  >
                    <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </button>
              </div>
              <div class="site-header__dropdown" :class="{ 'is-open': mobileSubOpen[link.label] }">
                <router-link
                  v-for="child in link.children"
                  :key="child.label"
                  class="site-header__dropdown-link"
                  :to="child.to"
                >
                  {{ child.label }}
                </router-link>
              </div>
            </div>
            <router-link v-else class="site-header__nav-link" :to="link.to">
              {{ link.label }}
            </router-link>
          </template>
        </nav>
        <!-- Phone only: search folds in here, where the bar has room for the
             language toggle alone. Socials live in the menu at every width
             below desktop; on desktop `display: contents` lifts them into
             the bar alongside the other utilities. -->
        <HeaderSearch v-if="isPhone" @submit="submitSearch" />
        <HeaderSocial />
        <router-link class="site-header__cta" to="/kontakt">{{ t('header.contact') }}</router-link>
      </div>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: var(--shadow-sm);
}

.site-header__inner {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-height: 76px;
  padding-inline: var(--space-4);
}

.site-header__brand {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-right: var(--space-2);
}

.site-header__logo {
  height: 56px;
  width: auto;
  display: block;
}

.site-header__nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-1) 18px;
  flex: 1;
  min-width: 0;
}

.site-header__nav-link {
  position: relative;
  color: var(--color-text);
  text-decoration: none;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  white-space: nowrap;
  padding-bottom: 6px;
  border-bottom: 1.5px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.site-header__nav-link:hover {
  color: var(--color-primary);
}

.site-header__nav-link.router-link-exact-active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.site-header__nav-item--dropdown {
  position: relative;
}

.site-header__nav-item-row {
  display: flex;
  align-items: center;
  gap: 2px;
}

.site-header__nav-subtoggle {
  display: none;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0;
}

.site-header__nav-subtoggle svg {
  transition: transform 0.15s ease;
}

.site-header__nav-subtoggle svg.is-open {
  transform: rotate(180deg);
}

.site-header__dropdown {
  display: none;
}

.site-header__dropdown-link {
  color: var(--color-text);
  text-decoration: none;
  white-space: nowrap;
}

.site-header__utils {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.lang {
  position: relative;
  display: flex;
  flex-shrink: 0;
  padding: 3px;
  border-radius: 999px;
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border);
  transition: border-color 0.15s ease;
}

.lang:hover {
  border-color: var(--color-primary);
}

/* The pill that slides between the two segments. It sits behind the labels and
   is sized to half the control minus the padding on both sides. */
.lang__indicator {
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 3px);
  height: calc(100% - 6px);
  border-radius: 999px;
  background: var(--color-primary);
  box-shadow: 0 1px 3px rgba(23, 33, 28, 0.18);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.lang__indicator--end {
  transform: translateX(100%);
}

.lang__option {
  position: relative;
  min-width: 38px;
  padding: 5px 10px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--color-text-muted);
  font: inherit;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.4px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.lang__option:hover:not(.lang__option--active) {
  color: var(--color-primary-dark);
}

.lang__option--active {
  color: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .lang__indicator {
    transition: none;
  }
}

.site-header__cta {
  flex-shrink: 0;
  background: var(--color-primary);
  color: #ffffff;
  text-decoration: none;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  padding: 11px 22px;
  border-radius: 999px;
  margin-right: var(--space-2);
  transition: background 0.15s ease;
}

.site-header__cta:hover {
  background: var(--color-primary-dark);
}

.site-header__toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-left: auto;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-ink);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.site-header__toggle:hover {
  border-color: var(--color-primary);
}

.site-header__menu {
  display: contents;
}

@media (min-width: 1301px) {
  /* The menu is `display: contents` here, so nav and the CTA become flex
     items of the bar alongside brand and utils. Explicit order restores the
     intended reading order: brand · nav · search/lang/social · contact. */
  .site-header__brand {
    order: 1;
  }

  .site-header__nav {
    order: 2;
  }

  .site-header__utils {
    order: 3;
  }

  .site-header__social {
    order: 4;
  }

  .site-header__cta {
    order: 5;
  }

  .site-header__nav-item--dropdown:hover .site-header__dropdown,
  .site-header__nav-item--dropdown:focus-within .site-header__dropdown {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 12px;
    min-width: 200px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    padding: var(--space-2);
    z-index: 10;
  }

  .site-header__dropdown-link {
    padding: 9px 12px;
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
    font-weight: 600;
  }

  .site-header__dropdown-link:hover {
    background: var(--color-primary-light);
    color: var(--color-primary-dark);
  }
}

/* Between the burger breakpoint and roughly 1700px the full nav did not fit,
   so it wrapped onto a second row inside a bar sized for one -- which is most
   laptop widths (1366, 1440, 1536, 1600). Tightening the tracking and the gaps
   buys back the few dozen pixels it needs to stay on one line. */
@media (min-width: 1301px) and (max-width: 1699px) {
  .site-header__nav {
    flex-wrap: nowrap;
    gap: 0 11px;
  }

  .site-header__nav-link {
    font-size: 0.69rem;
    letter-spacing: 0.1px;
  }

  .site-header__inner {
    gap: var(--space-3);
  }

  .site-header__search {
    width: 132px;
  }

  .site-header__search:focus-within {
    width: 150px;
  }
}

@media (max-width: 1300px) {
  .site-header__toggle {
    display: flex;
  }

  .site-header__inner {
    position: relative;
    padding-inline: var(--space-3);
  }

  .site-header__logo {
    height: 44px;
  }

  .site-header__menu {
    display: none;
  }

  .site-header__menu.is-open {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-4);
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    max-height: calc(100vh - 76px);
    overflow-y: auto;
    background: var(--color-bg);
    border-top: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
    padding: var(--space-4) var(--space-3);
  }

  .site-header__nav {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .site-header__nav-link {
    font-size: 0.85rem;
  }

  .site-header__nav-item--dropdown {
    width: 100%;
  }

  .site-header__nav-item-row {
    width: 100%;
  }

  .site-header__nav-item-row .site-header__nav-link {
    flex: 1;
  }

  .site-header__nav-subtoggle {
    display: inline-flex;
    width: 30px;
    height: 30px;
  }

  .site-header__dropdown {
    flex-direction: column;
    gap: var(--space-2);
    padding-left: var(--space-3);
    margin-top: var(--space-2);
  }

  .site-header__dropdown.is-open {
    display: flex;
  }

  .site-header__dropdown-link {
    font-size: 0.8rem;
    color: var(--color-text-muted);
  }

  /* Utils sit at the right of the bar, just before the hamburger. */
  .site-header__utils {
    margin-left: auto;
    gap: var(--space-2);
  }

  .site-header__toggle {
    margin-left: 0;
  }

  .site-header__cta {
    margin-right: 0;
    text-align: center;
  }
}
</style>
