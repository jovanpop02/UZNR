"""Fills the English fields of content that is already in the database.

The other import commands only write English on the rows they create, so a
database that was seeded before the translations existed — every local install,
and any environment whose data outlived a deploy — stays Montenegrin-only. This
command reads the same seed files and copies across nothing but the `*_en`
fields, matching rows by their Montenegrin text (slug, title, heading), so no
other content is touched and nothing is duplicated.

Safe to re-run. By default an English field that already has something in it is
left alone, so a translation corrected in the admin survives; pass --overwrite
to replace admin edits with what the seed files say.

    python manage.py import_translations
    python manage.py import_translations --overwrite
    python manage.py import_translations --dry-run

Document titles are deliberately left in Montenegrin: laws, rulebooks and
publications are cited by their official names, so the seed files carry no
`title_en` for them and this command has nothing to write.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import (
    Announcement,
    AnnouncementLink,
    ImportantLink,
    NewsItem,
    Page,
    PageSection,
    SectionItem,
)

DATA_DIR = Path(__file__).resolve().parents[2] / 'seed_data'
PAGES_DIR = DATA_DIR / 'pages'

#: projekti_biblioteka.json holds two pages in one file, keyed by page slug.
GROUPED_PAGES = ('projekti', 'biblioteka')


class Command(BaseCommand):
    help = 'Prenosi engleske prevode iz seed fajlova na postojeći sadržaj u bazi.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite', action='store_true',
            help='Prepiši i polja koja već imaju engleski tekst.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Samo prikaži šta bi bilo promijenjeno.',
        )

    def handle(self, *args, **options):
        self.overwrite = options['overwrite']
        self.dry_run = options['dry_run']
        self.updated = 0
        self.missing = []

        with transaction.atomic():
            self.news()
            self.announcements()
            self.important_links()
            self.pages()
            self.grouped_pages()
            if self.dry_run:
                transaction.set_rollback(True)

        for note in self.missing:
            self.stdout.write(self.style.WARNING(f'  nema u bazi: {note}'))
        verb = 'Bilo bi izmijenjeno' if self.dry_run else 'Izmijenjeno'
        self.stdout.write(self.style.SUCCESS(f'{verb}: {self.updated} zapisa'))

    # -- helpers ---------------------------------------------------------

    def apply(self, obj, source, fields, label):
        """Copy `fields` ('excerpt_en', …) from a seed dict onto a model row."""
        changed = []
        for field in fields:
            value = (source.get(field) or '').strip()
            if not value:
                continue
            if getattr(obj, field) and not self.overwrite:
                continue
            if getattr(obj, field) == value:
                continue
            setattr(obj, field, value)
            changed.append(field)
        if not changed:
            return
        obj.save(update_fields=changed)
        self.updated += 1
        self.stdout.write(f'  {label}: {", ".join(changed)}')

    def load(self, path):
        return json.loads(path.read_text(encoding='utf-8'))

    # -- sources ---------------------------------------------------------

    def news(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nVIJESTI'))
        by_slug = {item.slug: item for item in NewsItem.objects.all()}
        for entry in self.load(DATA_DIR / 'news.json'):
            item = by_slug.get(entry['slug'])
            if item is None:
                self.missing.append(f"vijest „{entry['slug']}“")
                continue
            self.apply(item, entry, ('title_en', 'excerpt_en', 'content_en'), entry['slug'])

    def announcements(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nOGLASI'))
        for entry in self.load(DATA_DIR / 'announcements.json'):
            obj = Announcement.objects.filter(title=entry['title']).first()
            if obj is None:
                self.missing.append(f"oglas „{entry['title'][:50]}“")
                continue
            self.apply(obj, entry, ('title_en', 'excerpt_en', 'link_label_en'), entry['title'][:50])
            for link_spec in entry.get('links') or []:
                link = obj.links.filter(title=link_spec['title']).first()
                if link is not None:
                    self.apply(link, link_spec, ('title_en',), f"  {link_spec['title'][:50]}")

    def important_links(self):
        self.stdout.write(self.style.MIGRATE_HEADING('\nVAŽNI LINKOVI'))
        for entry in self.load(DATA_DIR / 'important_links.json'):
            obj = ImportantLink.objects.filter(title=entry['title']).first()
            if obj is None:
                self.missing.append(f"link „{entry['title'][:50]}“")
                continue
            self.apply(obj, entry, ('title_en',), entry['title'][:50])

    def pages(self):
        for path in sorted(PAGES_DIR.glob('*.json')):
            data = self.load(path)
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n{data['slug'].upper()}"))
            page = Page.objects.filter(slug=data['slug']).first()
            if page is None:
                self.missing.append(f"stranica „{data['slug']}“")
                continue
            self.apply(page, data, ('title_en', 'intro_en'), data['slug'])
            for section_data in data.get('sections', []):
                self.section(page, section_data)

    def grouped_pages(self):
        data = self.load(DATA_DIR / 'projekti_biblioteka.json')
        for slug in GROUPED_PAGES:
            self.stdout.write(self.style.MIGRATE_HEADING(f'\n{slug.upper()}'))
            page = Page.objects.filter(slug=slug).first()
            if page is None:
                self.missing.append(f'stranica „{slug}“')
                continue
            for block in data.get(slug, []):
                self.section(page, block)

    def section(self, page, section_data):
        """One block of a page, plus the items inside it.

        Blocks are matched on their Montenegrin heading, which is what the two
        seeding commands already use as a block's identity. A heading-less block
        (the single flat list most pages hold) is matched as the page's only one.
        """
        heading = section_data.get('heading', '')
        sections = page.sections.filter(heading=heading)
        section = sections.first()
        if section is None or sections.count() > 1:
            self.missing.append(f'sekcija „{heading[:50]}“ na stranici {page.slug}')
            return
        self.apply(section, section_data, ('heading_en', 'body_en'), heading[:50] or f'({page.slug})')

        for item_data in section_data.get('items', []):
            item = section.items.filter(title=item_data['title']).first()
            if item is None:
                self.missing.append(f"stavka „{item_data['title'][:50]}“")
                continue
            self.apply(
                item, item_data,
                ('title_en', 'description_en', 'reference_en'),
                f"  {item_data['title'][:50]}",
            )
