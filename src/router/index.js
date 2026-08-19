import { createRouter, createWebHistory } from 'vue-router'
import { isPageLoading } from '../loading'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../pages/HomePage.vue') },
    { path: '/o-nama', component: () => import('../pages/OnamaPage.vue') },
    { path: '/regulativa', component: () => import('../pages/RegulativaPage.vue') },
    { path: '/projekti', component: () => import('../pages/ProjektiPage.vue') },
    { path: '/oglasi', component: () => import('../pages/OglasiPage.vue') },
    { path: '/publikacije', component: () => import('../pages/PublikacijePage.vue') },
    { path: '/biblioteka', component: () => import('../pages/BibliotekaPage.vue') },
    { path: '/press', component: () => import('../pages/PressPage.vue') },
    { path: '/pitanja-odgovori', component: () => import('../pages/PitanjaOdgovoriPage.vue') },
    { path: '/arhiva', component: () => import('../pages/ArhivaPage.vue') },
    { path: '/vijesti/:slug', component: () => import('../pages/NewsDetailPage.vue') },
    { path: '/kontakt', component: () => import('../pages/KontaktPage.vue') },
    // Catch-all. Without it an unknown address rendered the header and footer
    // around an empty router-view, which is what every mistyped or stale link
    // landed on once Netlify rewrote it to index.html.
    { path: '/:pathMatch(.*)*', component: () => import('../pages/NotFoundPage.vue') },
  ],
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

router.beforeEach(() => {
  isPageLoading.value = true
})

router.afterEach(() => {
  isPageLoading.value = false
})

router.onError(() => {
  isPageLoading.value = false
})

export default router
