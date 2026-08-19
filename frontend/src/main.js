import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import i18n, { setLocale } from './i18n'
import reveal from './reveal'

setLocale(i18n.global.locale.value)

createApp(App).use(router).use(i18n).directive('reveal', reveal).mount('#app')
