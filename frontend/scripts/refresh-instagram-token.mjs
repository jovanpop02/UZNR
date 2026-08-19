// Exchanges the current long-lived Instagram token for a fresh 60-day one.
//
// Long-lived tokens expire ~60 days after issue, and an expired token means the
// build quietly stops refreshing posts (it falls back to the committed list, so
// the site keeps working — it just goes stale). Run this before expiry:
//
//   INSTAGRAM_TOKEN=<current token> npm run refresh-instagram-token
//
// then paste the printed token into Netlify's INSTAGRAM_TOKEN variable.
//
// The token must be at least 24 hours old for Instagram to refresh it.

const TOKEN = process.env.INSTAGRAM_TOKEN

if (!TOKEN) {
  console.error('Set INSTAGRAM_TOKEN to the current long-lived token first.')
  process.exit(1)
}

const url = new URL('https://graph.instagram.com/refresh_access_token')
url.searchParams.set('grant_type', 'ig_refresh_token')
url.searchParams.set('access_token', TOKEN)

const res = await fetch(url)
const data = await res.json()

if (!res.ok || data.error) {
  console.error('Refresh failed:', data?.error?.message || `HTTP ${res.status}`)
  process.exit(1)
}

const days = Math.round((data.expires_in || 0) / 86400)
console.log('\nNew token (paste into Netlify → INSTAGRAM_TOKEN):\n')
console.log(data.access_token)
console.log(`\nValid for ~${days} days.\n`)
