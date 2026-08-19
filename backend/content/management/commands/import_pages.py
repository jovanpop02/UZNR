"""Seeds the page CMS from content/seed_data/pages/*.json.

The JSON is produced by the frontend's `scripts/export-page-content.mjs` from
the content that used to be hardcoded there, so a fresh install has a populated
admin instead of empty pages.

Safe to re-run: a page that already exists is left alone unless --replace is
passed, so this never silently overwrites something staff edited in the admin.

    python manage.py import_pages
    python manage.py import_pages --replace regulativa
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Page, PageSection, SectionItem

SEED_DIR = Path(__file__).resolve().parents[2] / 'seed_data' / 'pages'

# Documents and images referenced by the exported JSON are served by the
# frontend out of its own `public/` folder (e.g. /documents/regulativa/zakon.pdf).
# Seeded items keep pointing at those paths; files uploaded later through the
# admin land in media/ as normal.
FRONTEND_ASSET_PREFIXES = ('/documents/', '/press/', '/assets/')


class Command(BaseCommand):
    help = 'Loads page content (sections, links, documents) from the seed JSON.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            nargs='*',
            metavar='SLUG',
            help='Re-import these pages, discarding their current sections. '
                 'Pass with no slugs to replace every seeded page.',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        replace_all = replace is not None and len(replace) == 0
        replace_slugs = set(replace or [])

        files = sorted(SEED_DIR.glob('*.json'))
        if not files:
            self.stdout.write(self.style.WARNING(f'No seed files in {SEED_DIR}.'))
            return

        for path in files:
            data = json.loads(path.read_text(encoding='utf-8'))
            slug = data['slug']
            should_replace = replace_all or slug in replace_slugs

            page = Page.objects.filter(slug=slug).first()
            if page and not should_replace:
                self.stdout.write(f'{slug}: already exists, skipped (use --replace {slug} to reload)')
                continue

            with transaction.atomic():
                if page:
                    page.sections.all().delete()
                else:
                    page = Page(slug=slug)

                page.title = data['title']
                page.title_en = data.get('title_en', '')
                page.intro = data.get('intro', '')
                page.intro_en = data.get('intro_en', '')
                page.save()

                items_created = 0
                for section_data in data.get('sections', []):
                    section = PageSection.objects.create(
                        page=page,
                        kind=section_data.get('kind', PageSection.Kind.TEXT),
                        heading=section_data.get('heading', ''),
                        heading_en=section_data.get('heading_en', ''),
                        body=section_data.get('body', ''),
                        body_en=section_data.get('body_en', ''),
                        order=section_data.get('order', 0),
                    )
                    for item_data in section_data.get('items', []):
                        SectionItem.objects.create(
                            section=section,
                            title=item_data['title'],
                            title_en=item_data.get('title_en', ''),
                            description=item_data.get('description', ''),
                            description_en=item_data.get('description_en', ''),
                            url=self._as_url(item_data),
                            image_url=item_data.get('image', ''),
                            reference=item_data.get('reference', ''),
                            reference_en=item_data.get('reference_en', ''),
                            date_label=item_data.get('date_label', ''),
                            pages=item_data.get('pages'),
                            size_kb=item_data.get('size_kb'),
                            order=item_data.get('order', 0),
                        )
                        items_created += 1

            verb = 'replaced' if should_replace else 'created'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{slug}: {verb} — {len(data.get("sections", []))} sections, {items_created} items'
                )
            )

    @staticmethod
    def _as_url(item_data):
        """Seed items reference either an external link or a frontend asset path.

        Both go in `url`: FileField would need the bytes copied into media/, and
        these files are already published by the frontend.
        """
        url = item_data.get('url') or ''
        asset = item_data.get('file') or item_data.get('image') or ''
        if not url and asset.startswith(FRONTEND_ASSET_PREFIXES):
            return asset
        return url
