<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  variant: {
    type: String,
    required: true,
    validator: (v) => ['not-found', 'empty-archive', 'mission', 'network', 'osha-hardhat', 'osha-warning'].includes(v),
  },
})
</script>

<template>
  <svg
    v-if="variant === 'osha-hardhat'"
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altHardhat')"
  >
    <ellipse cx="200" cy="292" rx="150" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- wrench resting behind, diagonal -->
    <g transform="translate(88 208) rotate(-32)">
      <rect x="0" y="0" width="150" height="16" rx="8" fill="var(--illu-line-soft)" />
      <circle cx="6" cy="8" r="16" fill="none" stroke="var(--illu-line-soft)" stroke-width="10" />
    </g>

    <!-- vest, laid flat like a folded garment -->
    <g transform="translate(80 176)">
      <path d="M0 20 Q0 0 20 0 H100 Q120 0 120 20 L120 78 Q60 92 0 78 Z" fill="var(--illu-accent-warm)" />
      <path d="M0 20 L28 0 M120 20 L92 0" stroke="var(--illu-accent-warm-dark)" stroke-width="3" fill="none" />
      <line x1="30" y1="6" x2="30" y2="84" stroke="var(--illu-primary-tint)" stroke-width="11" stroke-linecap="round" opacity="0.9" />
      <line x1="90" y1="6" x2="90" y2="84" stroke="var(--illu-primary-tint)" stroke-width="11" stroke-linecap="round" opacity="0.9" />
    </g>

    <!-- hard hat, large and centered, resting on the vest -->
    <g transform="translate(102 66)">
      <ellipse cx="98" cy="132" rx="98" ry="16" fill="var(--illu-shadow)" opacity="0.4" />
      <path d="M8 118 Q8 4 98 4 Q188 4 188 118 Z" fill="var(--illu-helmet)" />
      <path d="M98 4 Q188 4 188 118 L140 118 Q132 30 98 4 Z" fill="var(--illu-helmet-dark)" opacity="0.35" />
      <ellipse cx="98" cy="118" rx="120" ry="18" fill="var(--illu-helmet-dark)" />
      <line x1="98" y1="0" x2="98" y2="70" stroke="var(--illu-helmet-dark)" stroke-width="5" stroke-linecap="round" opacity="0.5" />
      <circle cx="98" cy="0" r="8" fill="var(--illu-helmet-dark)" />
    </g>

    <!-- clipboard badge, document lines only -->
    <g transform="translate(266 178)">
      <rect x="0" y="0" width="80" height="64" rx="10" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="3" />
      <rect x="20" y="-8" width="40" height="16" rx="6" fill="var(--illu-primary)" />
      <line x1="14" y1="24" x2="66" y2="24" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
      <line x1="14" y1="38" x2="66" y2="38" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
      <line x1="14" y1="52" x2="46" y2="52" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
    </g>
  </svg>

  <svg
    v-else-if="variant === 'osha-warning'"
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altWarning')"
  >
    <ellipse cx="200" cy="292" rx="150" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- warning triangle -->
    <g>
      <path d="M200 44 L300 224 H100 Z" fill="var(--illu-accent-warm)" stroke="var(--illu-accent-warm-dark)" stroke-width="6" stroke-linejoin="round" />
      <rect x="192" y="104" width="16" height="66" rx="8" fill="#fff" />
      <circle cx="200" cy="192" r="10" fill="#fff" />
    </g>

    <!-- hard hat resting bottom-left -->
    <g transform="translate(46 210)">
      <path d="M4 48 Q4 2 42 2 Q80 2 80 48 Z" fill="var(--illu-helmet)" />
      <ellipse cx="42" cy="48" rx="50" ry="11" fill="var(--illu-helmet-dark)" />
      <line x1="42" y1="0" x2="42" y2="30" stroke="var(--illu-helmet-dark)" stroke-width="3.5" stroke-linecap="round" opacity="0.55" />
      <circle cx="42" cy="0" r="5" fill="var(--illu-helmet-dark)" />
    </g>

    <!-- safety goggles bottom-right -->
    <g transform="translate(286 216)">
      <circle cx="16" cy="20" r="20" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="4" />
      <circle cx="60" cy="20" r="20" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="4" />
      <rect x="30" y="14" width="12" height="10" fill="var(--illu-line)" />
      <ellipse cx="16" cy="20" rx="12" ry="12" fill="var(--illu-primary-tint)" opacity="0.6" />
      <ellipse cx="60" cy="20" rx="12" ry="12" fill="var(--illu-primary-tint)" opacity="0.6" />
    </g>

  </svg>

  <svg
    v-else-if="variant === 'not-found'"
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altNotFound')"
  >
    <ellipse cx="200" cy="288" rx="140" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- clipboard -->
    <g>
      <rect x="120" y="90" width="120" height="150" rx="14" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="3" />
      <rect x="152" y="80" width="56" height="22" rx="8" fill="var(--illu-primary)" />
      <line x1="142" y1="132" x2="222" y2="132" stroke="var(--illu-line-soft)" stroke-width="6" stroke-linecap="round" />
      <line x1="142" y1="156" x2="222" y2="156" stroke="var(--illu-line-soft)" stroke-width="6" stroke-linecap="round" />
      <line x1="142" y1="180" x2="196" y2="180" stroke="var(--illu-line-soft)" stroke-width="6" stroke-linecap="round" />
    </g>

    <!-- magnifying glass -->
    <g transform="translate(228 168) rotate(12)">
      <circle cx="0" cy="0" r="34" fill="var(--illu-glass)" fill-opacity="0.35" stroke="var(--illu-primary-dark)" stroke-width="7" />
      <line x1="24" y1="24" x2="54" y2="54" stroke="var(--illu-primary-dark)" stroke-width="9" stroke-linecap="round" />
    </g>

    <!-- question mark badge -->
    <circle cx="278" cy="96" r="24" fill="var(--illu-primary)" />
    <text x="278" y="105" text-anchor="middle" font-size="26" font-weight="700" fill="#fff" font-family="inherit">?</text>

    <!-- little safety helmet resting to the side -->
    <g transform="translate(96 226)">
      <path d="M4 30 Q4 -10 34 -10 Q64 -10 64 30 Z" fill="var(--illu-helmet)" />
      <ellipse cx="34" cy="30" rx="42" ry="8" fill="var(--illu-helmet-dark)" />
      <line x1="34" y1="-8" x2="34" y2="18" stroke="var(--illu-helmet-dark)" stroke-width="3" stroke-linecap="round" opacity="0.55" />
      <circle cx="34" cy="-8" r="4" fill="var(--illu-helmet-dark)" />
    </g>
  </svg>

  <svg
    v-else-if="variant === 'empty-archive'"
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altEmptyArchive')"
  >
    <ellipse cx="200" cy="288" rx="140" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- filing box -->
    <g>
      <rect x="110" y="150" width="180" height="100" rx="10" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="3" />
      <path d="M110 150 L140 108 H260 L290 150 Z" fill="var(--illu-primary-tint)" stroke="var(--illu-line)" stroke-width="3" />
      <rect x="176" y="132" width="48" height="14" rx="4" fill="var(--illu-primary)" />
    </g>

    <!-- floating folder with checkmark -->
    <g transform="translate(226 60)">
      <rect x="0" y="10" width="72" height="54" rx="8" fill="var(--illu-primary)" />
      <path d="M0 24 L14 10 H50 L58 24 Z" fill="var(--illu-primary-dark)" />
      <circle cx="36" cy="38" r="16" fill="#fff" />
      <path d="M28 38 L34 44 L46 30" stroke="var(--illu-primary-dark)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    </g>

    <!-- simple person, arm resting on box -->
    <g transform="translate(60 118)">
      <circle cx="34" cy="20" r="20" fill="var(--illu-skin)" />
      <path d="M4 118 Q4 62 34 62 Q64 62 64 118 Z" fill="var(--illu-accent-warm)" />
      <rect x="14" y="4" width="40" height="18" rx="9" fill="var(--illu-ink)" />
    </g>
  </svg>

  <svg
    v-else-if="variant === 'mission'"
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altMission')"
  >
    <ellipse cx="200" cy="292" rx="150" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- shield with check -->
    <g transform="translate(232 62)">
      <path d="M40 0 L80 16 V56 Q80 100 40 118 Q0 100 0 56 V16 Z" fill="var(--illu-primary)" />
      <path d="M22 58 L35 72 L60 40" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    </g>

    <!-- worker figure, hard hat + vest, standing confidently -->
    <g transform="translate(90 96)">
      <!-- legs -->
      <rect x="18" y="150" width="20" height="56" rx="8" fill="var(--illu-ink)" />
      <rect x="52" y="150" width="20" height="56" rx="8" fill="var(--illu-ink)" />
      <!-- body / vest -->
      <path d="M8 92 Q8 60 45 60 Q82 60 82 92 L82 156 Q45 170 8 156 Z" fill="var(--illu-accent-warm)" />
      <path d="M30 66 L45 150 L60 66" stroke="var(--illu-primary-tint)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9" />
      <!-- arm raised, thumbs up -->
      <path d="M78 96 Q108 88 108 62" stroke="var(--illu-accent-warm)" stroke-width="18" stroke-linecap="round" fill="none" />
      <circle cx="110" cy="52" r="12" fill="var(--illu-skin)" />
      <!-- other arm -->
      <path d="M12 100 Q-6 118 2 148" stroke="var(--illu-accent-warm)" stroke-width="18" stroke-linecap="round" fill="none" />
      <!-- head -->
      <circle cx="45" cy="34" r="26" fill="var(--illu-skin)" />
      <!-- hard hat -->
      <path d="M14 32 Q14 -10 45 -10 Q76 -10 76 32 Z" fill="var(--illu-helmet)" />
      <ellipse cx="45" cy="32" rx="42" ry="9" fill="var(--illu-helmet-dark)" />
      <line x1="45" y1="-8" x2="45" y2="22" stroke="var(--illu-helmet-dark)" stroke-width="3" stroke-linecap="round" opacity="0.55" />
      <circle cx="45" cy="-8" r="4" fill="var(--illu-helmet-dark)" />
    </g>

    <!-- checklist card floating bottom-left -->
    <g transform="translate(38 190)">
      <rect x="0" y="0" width="86" height="70" rx="10" fill="var(--illu-surface)" stroke="var(--illu-line)" stroke-width="3" />
      <circle cx="16" cy="18" r="6" fill="var(--illu-primary)" />
      <line x1="30" y1="18" x2="70" y2="18" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
      <circle cx="16" cy="36" r="6" fill="var(--illu-primary)" />
      <line x1="30" y1="36" x2="70" y2="36" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
      <circle cx="16" cy="54" r="6" stroke="var(--illu-line)" stroke-width="3" fill="none" />
      <line x1="30" y1="54" x2="58" y2="54" stroke="var(--illu-line-soft)" stroke-width="5" stroke-linecap="round" />
    </g>
  </svg>

  <svg
    v-else
    class="safety-illustration"
    viewBox="0 0 400 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    :aria-label="t('safetyIllustration.altTeam')"
  >
    <ellipse cx="200" cy="292" rx="150" ry="14" fill="var(--illu-shadow)" />
    <circle cx="200" cy="150" r="140" fill="var(--illu-bg)" />

    <!-- safety shield, watching over the team -->
    <g transform="translate(200 18)">
      <path d="M0 0 L24 6 V28 Q24 46 0 54 Q-24 46 -24 28 V6 Z" fill="var(--illu-primary)" />
      <path d="M-10 24 L-2 33 L14 14" stroke="#fff" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    </g>

    <!-- three helmeted workers, standing together -->
    <g transform="translate(88 128)">
      <rect x="0" y="78" width="58" height="86" rx="20" fill="var(--illu-primary-tint)" />
      <circle cx="29" cy="50" r="23" fill="var(--illu-skin)" />
      <path d="M6 30 Q6 12 29 12 Q52 12 52 30 Z" fill="var(--illu-helmet-dark)" />
      <ellipse cx="29" cy="30" rx="30" ry="7" fill="var(--illu-helmet)" />
      <line x1="29" y1="10" x2="29" y2="24" stroke="var(--illu-helmet)" stroke-width="2.5" stroke-linecap="round" opacity="0.55" />
    </g>

    <g transform="translate(170 96)">
      <path d="M0 118 Q0 66 42 66 Q84 66 84 118 L84 160 Q42 173 0 160 Z" fill="var(--illu-accent-warm)" />
      <circle cx="42" cy="34" r="28" fill="var(--illu-skin)" />
      <path d="M10 32 Q10 -8 42 -8 Q74 -8 74 32 Z" fill="var(--illu-helmet-dark)" />
      <ellipse cx="42" cy="32" rx="40" ry="8" fill="var(--illu-helmet)" />
      <line x1="42" y1="-6" x2="42" y2="22" stroke="var(--illu-helmet)" stroke-width="3" stroke-linecap="round" opacity="0.55" />
    </g>

    <g transform="translate(254 128)">
      <rect x="0" y="78" width="58" height="86" rx="20" fill="var(--illu-primary-tint)" />
      <circle cx="29" cy="50" r="23" fill="var(--illu-skin)" />
      <path d="M6 30 Q6 12 29 12 Q52 12 52 30 Z" fill="var(--illu-helmet-dark)" />
      <ellipse cx="29" cy="30" rx="30" ry="7" fill="var(--illu-helmet)" />
      <line x1="29" y1="10" x2="29" y2="24" stroke="var(--illu-helmet)" stroke-width="2.5" stroke-linecap="round" opacity="0.55" />
    </g>
  </svg>
</template>

<style scoped>
.safety-illustration {
  --illu-bg: var(--color-primary-light);
  --illu-surface: #ffffff;
  --illu-primary: var(--color-primary);
  --illu-primary-dark: var(--color-accent-dark);
  --illu-primary-tint: #cdeed7;
  --illu-line: var(--color-border);
  --illu-line-soft: #d7ddd8;
  --illu-ink: var(--color-ink);
  --illu-skin: #f2c199;
  --illu-accent-warm: #f2a54a;
  --illu-accent-warm-dark: #d98a2f;
  --illu-helmet: #ffcc32;
  --illu-helmet-dark: #dba018;
  --illu-glass: #ffffff;
  --illu-shadow: rgba(23, 33, 28, 0.06);
  width: 100%;
  height: auto;
  display: block;
}
</style>
