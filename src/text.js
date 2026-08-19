// Display-side text normalisation for CMS copy.

// Acronyms that must keep their capitals when a SHOUTED title is folded back
// down to sentence case. Matched case-insensitively against whole words.
const ACRONYMS = [
  'UZNR', 'UZNRCG', 'EU', 'OSHA', 'EU-OSHA', 'ILO', 'JU', 'JZU', 'NVO', 'IPA',
  'MONSTAT', 'MUP', 'PDF', 'ZNR', 'BALcanOSH', 'ENETOSH', 'IOSH', 'CG',
]
const ACRONYM_BY_LOWER = new Map(ACRONYMS.map((a) => [a.toLowerCase(), a]))

// A title counts as SHOUTED when almost every cased letter in it is uppercase.
// Well-formed titles ("Okrugli sto – Mladi imaju glas") sit far below this, so
// they pass through untouched; only all-caps entries get rewritten.
const SHOUT_RATIO = 0.8
const SHOUT_MIN_LETTERS = 12

function isShouted(value) {
  const letters = value.match(/\p{L}/gu)
  if (!letters || letters.length < SHOUT_MIN_LETTERS) return false
  const upper = letters.filter((c) => c === c.toUpperCase() && c !== c.toLowerCase())
  return upper.length / letters.length >= SHOUT_RATIO
}

/**
 * Folds an ALL-CAPS CMS title back to sentence case, restoring known acronyms.
 *
 * This cannot recover proper nouns — "BIJELO POLJE" becomes "Bijelo polje", not
 * "Bijelo Polje" — so it is a safety net for shouted entries, not a substitute
 * for typing titles correctly in the admin. Titles that are already cased
 * sensibly are returned unchanged.
 */
export function normalizeTitle(value) {
  const title = (value ?? '').toString().trim()
  if (!title || !isShouted(title)) return title

  const lowered = title.toLocaleLowerCase('sr-Latn-ME')

  // Restore acronyms, then capitalise the first letter of each sentence.
  const withAcronyms = lowered.replace(/\p{L}[\p{L}\-]*/gu, (word) => {
    const known = ACRONYM_BY_LOWER.get(word)
    return known ?? word
  })

  // Uppercase the first cased letter overall, plus anything after . ! ? or a
  // quote that opens a title.
  let seenFirst = false
  return withAcronyms.replace(/\p{L}/gu, (char, index, whole) => {
    if (!seenFirst) {
      seenFirst = true
      return char.toLocaleUpperCase('sr-Latn-ME')
    }
    const before = whole.slice(0, index)
    if (/[.!?]\s+$/.test(before)) return char.toLocaleUpperCase('sr-Latn-ME')
    return char
  })
}
