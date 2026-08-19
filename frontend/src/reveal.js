// Scroll-reveal directive: elements fade/slide in the first time they enter
// the viewport. Usage:
//   v-reveal            → reveal on scroll
//   v-reveal="2"        → same, staggered by 2 steps (2 × 70ms)
//
// Respects prefers-reduced-motion: motion-sensitive visitors get the content
// immediately, with no transform or transition applied.

const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)')
const STAGGER_MS = 70

let observer = null

function getObserver() {
  if (observer) return observer
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue
        entry.target.classList.add('is-revealed')
        observer.unobserve(entry.target)
      }
    },
    // Fire slightly before the element is fully on screen so the motion
    // finishes about when the reader's eye arrives.
    { rootMargin: '0px 0px -10% 0px', threshold: 0.1 },
  )
  return observer
}

export default {
  mounted(el, binding) {
    if (REDUCED.matches || typeof IntersectionObserver === 'undefined') {
      el.classList.add('is-revealed')
      return
    }

    el.classList.add('reveal')

    const step = Number(binding.value) || 0
    if (step > 0) el.style.transitionDelay = `${step * STAGGER_MS}ms`

    getObserver().observe(el)
  },

  unmounted(el) {
    if (observer) observer.unobserve(el)
  },
}
