<script setup></script>

<template>
  <div class="site-header__social">
    <a href="https://www.facebook.com/uznr.me" target="_blank" rel="noopener" aria-label="Facebook">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M14 9h3V5h-3c-2.2 0-4 1.8-4 4v2H8v4h2v7h4v-7h3l1-4h-4v-2c0-.6.4-1 1-1z"/></svg>
    </a>
    <a href="https://www.instagram.com/uznr.me/" target="_blank" rel="noopener" aria-label="Instagram">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>
    </a>
    <a href="https://www.youtube.com/@udruzenjezastitenaraducrne2151" target="_blank" rel="noopener" aria-label="YouTube">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><rect x="2" y="6" width="20" height="12" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10 9.5l6 2.5-6 2.5z"/></svg>
    </a>
  </div>
</template>

<style scoped>
.site-header__social {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.site-header__social a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.site-header__social a:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

/* Tablet and below: rendered inside the collapsed menu panel. */
@media (max-width: 1300px) {
  .site-header__social {
    justify-content: center;
  }
}
</style>
