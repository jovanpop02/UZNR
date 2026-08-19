export function isIOS() {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent || ''
  const isAppleTouch = /iPad|iPhone|iPod/.test(ua)
  // iPadOS reports as "Macintosh" but exposes touch support, unlike a real Mac.
  const isIpadOS = navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1
  return isAppleTouch || isIpadOS
}
