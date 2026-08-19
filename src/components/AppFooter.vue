<script setup>
import { useI18n } from 'vue-i18n'
import logo from '../assets/uznr-logo.png'
import mekLogo from '../assets/footer-partner-mek.png'
import balcanoshLogo from '../assets/footer-partner-balcanosh.png'

const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__top">
      <div class="site-footer__logo-wrap">
        <img class="site-footer__visual-logo" :src="logo" alt="UZNR" />
      </div>

      <div class="site-footer__grid">
        <div class="site-footer__col site-footer__col--brand">
          <p class="site-footer__brand">UZNR</p>
          <p class="site-footer__blurb">
            {{ t('footer.blurb') }}
          </p>
          <div class="site-footer__social">
            <a href="https://www.facebook.com/uznr.me" target="_blank" rel="noopener" aria-label="Facebook">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M14 9h3V5h-3c-2.2 0-4 1.8-4 4v2H8v4h2v7h4v-7h3l1-4h-4v-2c0-.6.4-1 1-1z"/></svg>
            </a>
            <a href="https://www.instagram.com/uznr.me/" target="_blank" rel="noopener" aria-label="Instagram">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>
            </a>
            <a href="https://www.youtube.com/@udruzenjezastitenaraducrne2151" target="_blank" rel="noopener" aria-label="YouTube">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><rect x="2" y="6" width="20" height="12" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.5l6 2.5-6 2.5z"/></svg>
            </a>
          </div>
        </div>

        <div class="site-footer__info-group">
          <div class="site-footer__col">
            <p class="site-footer__heading">{{ t('footer.addressHeading') }}</p>
            <p class="site-footer__text">4. jul 109/3<br />81000 Podgorica<br />Crna Gora</p>
          </div>

          <div class="site-footer__col">
            <p class="site-footer__heading">{{ t('footer.contactHeading') }}</p>
            <p class="site-footer__text">
              <a class="site-footer__link" href="mailto:info@uznr.me">info@uznr.me</a><br />
              <a class="site-footer__link" href="tel:+38267412900">+382 67 412 900</a><br />
              <a class="site-footer__link" href="tel:+38220671340">+382 20 671 340</a>
            </p>
          </div>

          <div class="site-footer__col">
            <p class="site-footer__heading">{{ t('footer.hoursHeading') }}</p>
            <p class="site-footer__text">{{ t('footer.hoursDays') }}<br />8:00 – 16:00</p>
          </div>
        </div>
      </div>

      <div class="site-footer__partners">
        <a href="https://www.gov.me/mek" target="_blank" rel="noopener">
          <img class="site-footer__partner-logo" :src="mekLogo" alt="Ministarstvo ekonomskog razvoja" />
        </a>
        <a href="https://project-balcanosh.net/" target="_blank" rel="noopener">
          <img class="site-footer__partner-logo" :src="balcanoshLogo" alt="BALcanOSH" />
        </a>
      </div>
    </div>

    <div class="site-footer__bottom">
      <div class="container site-footer__bottom-inner">
        <p class="site-footer__copyright">© {{ year }} Udruženje zaštite na radu Crne Gore. {{ t('footer.copyrightSuffix') }}</p>
        <!-- Storyset's free licence requires a visible credit wherever their
             illustrations are used. Remove this only if the licence is bought. -->
        <p class="site-footer__credit">
          <a href="https://storyset.com/" target="_blank" rel="noopener">Ilustracije: Storyset</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  border-top: 1px solid var(--color-border);
  background: var(--color-ink);
  color: rgba(255, 255, 255, 0.75);
}

.site-footer__top {
  padding-block: var(--space-8);
  display: grid;
  grid-template-columns: 220px 1fr;
  grid-template-areas:
    'logo grid'
    'partners grid';
  align-items: start;
  gap: var(--space-5) var(--space-8);
}

.site-footer__logo-wrap {
  grid-area: logo;
  display: flex;
}

.site-footer__visual-logo {
  height: 92px;
  width: auto;
}

.site-footer__grid {
  grid-area: grid;
  min-width: 0;
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: var(--space-5);
}

.site-footer__col--brand {
  padding-right: var(--space-4);
}

.site-footer__info-group {
  display: contents;
}

.site-footer__brand {
  color: #fff;
  font-weight: 700;
  margin-bottom: var(--space-1);
}

.site-footer__blurb {
  max-width: 320px;
  font-size: 0.9rem;
  margin-bottom: var(--space-3);
}

.site-footer__social {
  display: flex;
  gap: var(--space-2);
}

.site-footer__social a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.75);
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.site-footer__social a:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.site-footer__heading {
  color: #fff;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
}

.site-footer__text {
  font-size: 0.9rem;
  line-height: 1.7;
}

.site-footer__link {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
}

.site-footer__link:hover {
  color: #fff;
  text-decoration: underline;
}

.site-footer__partners {
  grid-area: partners;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  width: 100%;
}

.site-footer__partner-logo {
  height: 44px;
  width: auto;
  max-width: 160px;
  object-fit: contain;
  filter: grayscale(1) brightness(0) invert(1);
  opacity: 0.7;
  transition: opacity 0.15s ease;
}

.site-footer__partner-logo:hover {
  opacity: 1;
}

.site-footer__bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.site-footer__bottom-inner {
  padding-block: var(--space-3);
}

.site-footer__bottom-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2) var(--space-4);
}

.site-footer__copyright,
.site-footer__credit {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.site-footer__credit a {
  color: inherit;
  text-decoration: none;
}

.site-footer__credit a:hover {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: underline;
}

@media (max-width: 1100px) {
  .site-footer__grid {
    grid-template-columns: 1fr 1fr 1fr;
  }

  .site-footer__col--brand {
    grid-column: 1 / -1;
    padding-right: 0;
  }
}

@media (max-width: 900px) {
  .site-footer__top {
    grid-template-columns: 1fr;
    grid-template-areas:
      'logo'
      'grid'
      'partners';
    gap: var(--space-5);
    text-align: center;
  }

  .site-footer__logo-wrap {
    justify-content: center;
  }

  .site-footer__grid {
    grid-template-columns: 1fr;
    gap: var(--space-5);
    justify-items: center;
  }

  .site-footer__col--brand {
    padding-right: 0;
  }

  .site-footer__blurb {
    margin-inline: auto;
  }

  .site-footer__social {
    justify-content: center;
  }

  .site-footer__info-group {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: var(--space-4);
    width: 100%;
  }

  .site-footer__info-group .site-footer__col {
    flex: 1;
    min-width: 0;
  }

  .site-footer__partners {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 600px) {
  .site-footer__top {
    padding-block: var(--space-6);
  }
}

@media (max-width: 480px) {
  .site-footer__info-group {
    gap: var(--space-2);
  }

  .site-footer__info-group .site-footer__heading {
    font-size: 0.72rem;
  }

  .site-footer__info-group .site-footer__text {
    font-size: 0.8rem;
  }

  .site-footer__partner-logo {
    height: 36px;
  }

  .site-footer__social a {
    width: 38px;
    height: 38px;
  }
}
</style>
