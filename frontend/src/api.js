import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// The production API runs on Render's free tier, which spins the service down
// after ~15 minutes idle. The first request after that has to wait out a cold
// start — container boot, then `migrate`, then gunicorn — which can take the
// better part of a minute.
//
// Two consequences this module handles:
//
//  1. A bare fetch() has no timeout, so a request that never lands leaves the
//     caller stuck on `loading` forever and its error branch unreachable. Every
//     request gets an abort signal so failure is always reachable.
//  2. A wait that long looks identical to a broken site. `isWakingBackend` flips
//     on once a request has been outstanding longer than SLOW_AFTER_MS, so the
//     UI can explain what is happening instead of showing a frozen spinner.

const TIMEOUT_MS = 45000
const SLOW_AFTER_MS = 5000

// True while at least one request has been in flight longer than SLOW_AFTER_MS.
export const isWakingBackend = ref(false)

let pendingSlow = 0

function markSlow() {
  pendingSlow += 1
  isWakingBackend.value = true
}

function clearSlow() {
  pendingSlow = Math.max(0, pendingSlow - 1)
  if (pendingSlow === 0) isWakingBackend.value = false
}

export class ApiError extends Error {
  constructor(message, { path, status = 0, timedOut = false } = {}) {
    super(message)
    this.name = 'ApiError'
    this.path = path
    this.status = status
    this.timedOut = timedOut
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  let markedSlow = false
  const slowTimer = setTimeout(() => {
    markedSlow = true
    markSlow()
  }, SLOW_AFTER_MS)

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      signal: controller.signal,
      ...(body === undefined
        ? {}
        : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
    })
    if (!res.ok) {
      throw new ApiError(`API error ${res.status} on ${path}`, { path, status: res.status })
    }
    // 204s and empty bodies are valid responses; don't force them through JSON.
    const text = await res.text()
    return text ? JSON.parse(text) : null
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new ApiError(`Request to ${path} timed out`, { path, timedOut: true })
    }
    throw err instanceof ApiError ? err : new ApiError(err.message, { path })
  } finally {
    clearTimeout(timeout)
    clearTimeout(slowTimer)
    if (markedSlow) clearSlow()
  }
}

export function fetchAnnouncements() {
  return request('/api/announcements')
}

export function fetchNews() {
  return request('/api/news')
}

export function fetchNewsItem(slug) {
  return request(`/api/news/${slug}`)
}

export function fetchMembers() {
  return request('/api/members')
}

export function fetchImportantLinks() {
  return request('/api/important-links')
}

// Admin-editable content for one page, both languages in every text field.
export function fetchPage(slug) {
  return request(`/api/pages/${slug}`)
}

// Contact form. A 429 means the backend's rate limit kicked in, and a 400 means
// the payload failed server-side validation — both reach the caller as an
// ApiError carrying `status`, so the form can say which happened.
export function submitContactMessage(payload) {
  return request('/api/contact', { method: 'POST', body: payload })
}
