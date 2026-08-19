const EUPRAVA_PATTERN = /eUprav[a-zA-Zšđčćžа-я]*/i

export function splitExcerptForLink(text, item) {
  if (!item?.link) return [{ text, isLink: false }]

  const match = text.match(EUPRAVA_PATTERN)
  if (match) {
    const before = text.slice(0, match.index)
    const word = match[0]
    const after = text.slice(match.index + word.length)
    return [
      { text: before, isLink: false },
      { text: word, isLink: true },
      { text: after, isLink: false },
    ]
  }

  return [
    { text: text.endsWith(' ') ? text : `${text} `, isLink: false },
    { text: item.link_label || 'Više informacija', isLink: true },
  ]
}
