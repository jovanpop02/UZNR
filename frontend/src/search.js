import { primaryLegislation, bylawCategories } from './data/regulativa'
import { publications } from './data/publikacije'

// Lowercases and strips diacritics so "zastita" finds "zaštita". NFD splits
// č/ć/š/ž into base letter + combining mark, which the regex then drops; đ/Đ
// carry a stroke rather than a mark, so they are mapped by hand.
const COMBINING_MARKS = /\p{M}/gu
const D_STROKE = /đ/gu
const D_STROKE_UPPER = /Đ/gu

export function foldSearchText(value) {
  return (value ?? '')
    .toString()
    .normalize('NFD')
    .replace(COMBINING_MARKS, '')
    .replace(D_STROKE, 'd')
    .replace(D_STROKE_UPPER, 'D')
    .toLowerCase()
}

export function buildStaticSearchIndex() {
  const regulativaItems = [
    ...primaryLegislation,
    ...bylawCategories.flatMap((category) => category.items),
  ].map((item) => ({
    type: 'regulativa',
    typeLabel: 'Regulativa',
    title: item.title,
    meta: item.reference,
    file: item.file,
    sizeKb: item.sizeKb,
    routeTo: '/regulativa',
  }))

  const publikacijeItems = publications.map((pub) => ({
    type: 'publikacija',
    typeLabel: 'Publikacija',
    title: pub.title,
    meta: pub.dateLabel || null,
    file: pub.file,
    sizeKb: pub.sizeKb,
    routeTo: '/publikacije',
  }))

  return [...regulativaItems, ...publikacijeItems]
}

export function announcementsToSearchIndex(announcements) {
  return announcements.map((item) => ({
    type: 'oglas',
    typeLabel: 'Oglas',
    title: item.title,
    meta: item.is_open ? 'Otvoreno' : 'Isteklo',
    file: null,
    sizeKb: null,
    routeTo: '/oglasi',
  }))
}
