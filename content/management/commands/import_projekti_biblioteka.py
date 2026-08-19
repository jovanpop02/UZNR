"""Loads the Projekti and Biblioteka content into the database.

Both pages were built with their content hardcoded in the frontend, so their
admin entries started out empty. This reads a JSON dump of that content
(produced from `src/data/projekti.js` and `BibliotekaPage.vue`) and creates the
blocks and documents that make up each page.

Idempotent: a block is matched by its heading and a document by its address, so
running it twice does not duplicate anything, and content edited in the admin
afterwards is left alone.

    manage.py import_projekti_biblioteka dump.json --list
    manage.py import_projekti_biblioteka dump.json
    manage.py import_projekti_biblioteka dump.json --apply
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import Page, PageSection, SectionItem

#: dump key -> (page slug, Montenegrin title, English title)
PAGES = {
    'projekti': ('projekti', 'Projekti', 'Projects'),
    'biblioteka': ('biblioteka', 'Biblioteka', 'Library'),
}


class Command(BaseCommand):
    help = 'Uvozi sadržaj stranica Projekti i Biblioteka iz JSON dampa.'

    #: Shipped with the code so a deploy can seed a fresh database.
    DEFAULT_DUMP = (
        Path(__file__).resolve().parents[2] / 'seed_data' / 'projekti_biblioteka.json'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'dump', nargs='?', default=str(self.DEFAULT_DUMP),
            help='Putanja do JSON fajla. Podrazumijevano seed_data/projekti_biblioteka.json.',
        )
        parser.add_argument(
            '--apply', action='store_true',
            help='Sačuvaj. Bez ovoga se samo ispisuje šta bi bilo urađeno.',
        )
        parser.add_argument(
            '--list', action='store_true',
            help='Samo prikaži sadržaj dampa.',
        )

    def handle(self, *args, **options):
        path = Path(options['dump'])
        if not path.exists():
            raise CommandError(f'Nema fajla: {path}')

        data = json.loads(path.read_text(encoding='utf-8'))

        for key, (slug, title, title_en) in PAGES.items():
            blocks = data.get(key)
            if not blocks:
                self.stdout.write(self.style.WARNING(f'U dampu nema „{key}“ — preskačem.'))
                continue
            self.stdout.write(self.style.MIGRATE_HEADING(f'\n{slug.upper()}'))
            self.import_page(slug, title, title_en, blocks, options['apply'], options['list'])

        if not options['apply'] and not options['list']:
            self.stdout.write(self.style.WARNING(
                '\nNije sačuvano. Pokrenite ponovo sa --apply.'
            ))

    def import_page(self, slug, title, title_en, blocks, apply, list_only):
        # The page itself is created if missing. On Render the database is
        # rebuilt from scratch on every deploy and `import_pages` only knows
        # about the pages that have a seed file, so insisting the page already
        # exists would fail the boot rather than fill it in.
        page = Page.objects.filter(slug=slug).first()
        if page is None:
            if list_only or not apply:
                self.stdout.write(f'  (stranica „{slug}“ bi bila napravljena)')
                page = None
            else:
                page = Page.objects.create(slug=slug, title=title, title_en=title_en)

        created_blocks = created_items = skipped_items = 0

        for order, block in enumerate(blocks):
            heading = block['heading']
            items = block.get('items', [])
            self.stdout.write(f'  [{order}] {heading[:70]}  ({len(items)} dok.)')

            if list_only:
                continue

            # page is None only on a dry run for a page that does not exist yet,
            # in which case every block below counts as new.
            section = (
                PageSection.objects.filter(page=page, heading=heading).first()
                if page is not None
                else None
            )
            if section is None:
                created_blocks += 1
                if apply:
                    section = PageSection.objects.create(
                        page=page,
                        heading=heading,
                        heading_en=block.get('heading_en', ''),
                        body=block.get('body', ''),
                        body_en=block.get('body_en', ''),
                        kind=PageSection.Kind.DOCUMENTS,
                        order=order,
                    )

            for position, item in enumerate(items):
                # `section` is None on a dry run for a block that does not exist
                # yet, so there is nothing to check against — count it as new.
                exists = section is not None and SectionItem.objects.filter(
                    section=section, url=item['url']
                ).exists()
                if exists:
                    skipped_items += 1
                    continue
                created_items += 1
                if apply:
                    SectionItem.objects.create(
                        section=section,
                        title=item['title'],
                        url=item['url'],
                        pages=item.get('pages'),
                        size_kb=item.get('size_kb'),
                        order=position,
                    )

        if list_only:
            return

        verb = 'Napravljeno' if apply else 'Napravilo bi se'
        self.stdout.write(
            f'  → {verb}: {created_blocks} grupa, {created_items} dokumenata'
            + (f'; već postoji: {skipped_items}' if skipped_items else '')
        )

    def execute(self, *args, **options):
        # One transaction for the whole import: a half-loaded page is worse than
        # an empty one, because nobody can tell which half is missing.
        if options.get('apply'):
            with transaction.atomic():
                return super().execute(*args, **options)
        return super().execute(*args, **options)
