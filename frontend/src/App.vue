<script setup>
import { defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import PageLoader from './components/PageLoader.vue'

const { locale } = useI18n()

// The device-preview button opens the site in phone- and tablet-sized windows.
// That is a tool for building the site, not for reading it, so it never reaches
// visitors. The import is deliberately behind the flag rather than the template:
// a plain top-level import would still be bundled and shipped, only hidden.
// import.meta.env.DEV is replaced with a literal at build time, so the whole
// branch — component, its styles and the device list — is dropped.
const isDev = import.meta.env.DEV
const DevicePreviewSwitch = isDev
  ? defineAsyncComponent(() => import('./components/DevicePreviewSwitch.vue'))
  : null
</script>

<template>
  <PageLoader />
  <AppHeader />
  <main>
    <router-view v-slot="{ Component, route }">
      <transition name="page-fade" mode="out-in">
        <!-- Keying on locale as well as path makes a language switch
             cross-fade the page content instead of snapping it. -->
        <component :is="Component" :key="`${route.path}-${locale}`" />
      </transition>
    </router-view>
  </main>
  <AppFooter />
  <DevicePreviewSwitch v-if="isDev" />
</template>
