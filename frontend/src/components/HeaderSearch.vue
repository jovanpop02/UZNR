<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { fetchNews } from '../api'
import { localizeList } from '../cms'
import { buildStaticSearchIndex, foldSearchText } from '../search'
import { normalizeTitle } from '../text'

const MAX_SUGGESTIONS = 6
const MIN_QUERY = 2

const emit = defineEmits(['submit'])
const { t, locale } = useI18n()
const router = useRouter()

const query = ref('')
const open = ref(false)
const activeIndex = ref(-1)
const rootEl = ref(null)
const inputEl = ref(null)

// Documents and legislation ship with the bundle, so they are searchable on the
// first keystroke. News lives behind the API and is pulled once, lazily, the
// first time somebody actually types — the header is on every page and most
// visits never touch the search box.
const staticIndex = buildStaticSearchIndex()
// Raw API rows carry localised objects ({ mne, en }) rather than strings, so
// they go through localizeList before anything tries to match text against
// them. Kept raw, every title folds to "[object Object]" and matches nothing.
const rawNews = ref([])
const newsIndex = computed(() =>
  localizeList(rawNews.value, locale.value).map((item) => ({
    type: 'vijest',
    typeLabel: t('header.searchTypeNews'),
    title: item.title,
    meta: null,
    routeTo: `/vijesti/${item.slug}`,
  }))
)
let newsRequest = null

function loadNews() {
  if (newsRequest) return newsRequest
  newsRequest = fetchNews()
    .then((items) => {
      rawNews.value = items
    })
    .catch(() => {
      // A sleeping or unreachable backend just means no news suggestions; the
      // bundled documents still match, and Enter still reaches the archive.
      rawNews.value = []
    })
  return newsRequest
}

const suggestions = computed(() => {
  const q = foldSearchText(query.value.trim())
  if (q.length < MIN_QUERY) return []
  return [...newsIndex.value, ...staticIndex]
    .filter((item) => foldSearchText(item.title).includes(q))
    .slice(0, MAX_SUGGESTIONS)
})

const showPanel = computed(
  () => open.value && query.value.trim().length >= MIN_QUERY
)

watch(query, (value) => {
  activeIndex.value = -1
  if (value.trim().length >= MIN_QUERY) {
    open.value = true
    loadNews()
  }
})

function go(item) {
  open.value = false
  query.value = ''
  inputEl.value?.blur()
  router.push(item.routeTo)
}

function submit() {
  const picked = suggestions.value[activeIndex.value]
  if (picked) {
    go(picked)
    return
  }
  open.value = false
  emit('submit', query.value.trim())
}

// Arrow keys cycle through the options and back out to "nothing selected", so
// a reader can always get back to their raw query. Index -1 means no option is
// highlighted; shifting by one makes the wrap-around arithmetic straightforward.
function move(step) {
  if (!showPanel.value || !suggestions.value.length) return
  const slots = suggestions.value.length + 1
  const shifted = activeIndex.value + 1
  activeIndex.value = ((shifted + step + slots) % slots) - 1
}

function onEscape() {
  if (showPanel.value) {
    open.value = false
    activeIndex.value = -1
    return
  }
  query.value = ''
}

function onDocumentPointer(event) {
  if (rootEl.value && !rootEl.value.contains(event.target)) open.value = false
}

onMounted(() => document.addEventListener('pointerdown', onDocumentPointer))
onBeforeUnmount(() => document.removeEventListener('pointerdown', onDocumentPointer))
</script>

<template>
  <div ref="rootEl" class="header-search">
    <form
      class="site-header__search"
      role="search"
      @submit.prevent="submit"
    >
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.2" y2="16.2" stroke-linecap="round"/></svg>
      <input
        ref="inputEl"
        v-model="query"
        type="search"
        role="combobox"
        aria-autocomplete="list"
        aria-controls="header-search-listbox"
        :aria-expanded="showPanel"
        :aria-activedescendant="activeIndex >= 0 ? `header-search-opt-${activeIndex}` : undefined"
        :placeholder="t('header.searchPlaceholder')"
        :aria-label="t('header.searchPlaceholder')"
        @focus="open = true"
        @click="open = true"
        @keydown.down.prevent="move(1)"
        @keydown.up.prevent="move(-1)"
        @keydown.esc.prevent="onEscape"
      />
    </form>

    <div v-if="showPanel" class="header-search__panel">
      <ul
        v-if="suggestions.length"
        id="header-search-listbox"
        class="header-search__list"
        role="listbox"
        :aria-label="t('header.searchResults')"
      >
        <li
          v-for="(item, i) in suggestions"
          :id="`header-search-opt-${i}`"
          :key="item.routeTo + item.title"
          role="option"
          :aria-selected="i === activeIndex"
          class="header-search__option"
          :class="{ 'header-search__option--active': i === activeIndex }"
          @pointerenter="activeIndex = i"
          @click="go(item)"
        >
          <span class="header-search__type">{{ item.typeLabel }}</span>
          <span class="header-search__title">{{ normalizeTitle(item.title) }}</span>
        </li>
      </ul>
      <p v-else class="header-search__empty">
        {{ t('header.searchNoResults', { q: query.trim() }) }}
      </p>
      <button type="button" class="header-search__all" @click="submit">
        {{ t('header.searchSeeAll') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.header-search {
  position: relative;
  flex-shrink: 0;
}

.site-header__search {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  width: 168px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-text-muted);
  transition: border-color 0.15s ease, width 0.2s ease;
}

.site-header__search:focus-within {
  border-color: var(--color-primary);
  width: 200px;
}

.site-header__search input {
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.82rem;
  color: var(--color-ink);
  width: 100%;
  min-width: 0;
}

.site-header__search input::-webkit-search-cancel-button {
  cursor: pointer;
}

.header-search__panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 340px;
  max-width: 78vw;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  z-index: 60;
}

.header-search__list {
  list-style: none;
  margin: 0;
  padding: 4px;
  max-height: 320px;
  overflow-y: auto;
}

.header-search__option {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
}

.header-search__option--active {
  background: var(--color-primary-light);
}

.header-search__type {
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent-dark);
}

.header-search__title {
  font-size: 0.85rem;
  line-height: 1.35;
  color: var(--color-ink);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.header-search__empty {
  padding: 14px 12px;
  font-size: 0.84rem;
  color: var(--color-text-muted);
}

.header-search__all {
  display: block;
  width: 100%;
  padding: 9px 12px;
  border: none;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-alt);
  color: var(--color-accent-dark);
  font: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
}

.header-search__all:hover {
  background: var(--color-primary-light);
}

/* Tablet: the bar is tighter, so don't grow on focus. */
@media (max-width: 1300px) {
  .site-header__search {
    width: 150px;
  }

  .site-header__search:focus-within {
    width: 150px;
  }
}

/* Phone: rendered inside the collapsed menu, so it spans the panel and the
   suggestions drop straight underneath it at full width. */
@media (max-width: 600px) {
  .header-search {
    width: 100%;
  }

  .site-header__search,
  .site-header__search:focus-within {
    width: 100%;
  }

  .header-search__panel {
    width: 100%;
    max-width: none;
    left: 0;
    right: auto;
  }
}
</style>
