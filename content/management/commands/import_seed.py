import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from content.models import Announcement, AnnouncementLink, ImportantLink, Member, NewsImage, NewsItem

DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'seed_data'

SIZE_SUFFIX = re.compile(r'-\d+x\d+$')
ROTATED_SUFFIX = re.compile(r'-rotated$')


def download(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def filename_from_url(url):
    return Path(urlparse(url).path).name or 'file'


def photo_key(name):
    """Identity of the underlying photo, ignoring WordPress size variants.

    The old site serves one photo at several sizes, so `foo-876x600.jpg` (used
    as the thumbnail) and `foo-1536x1052.jpg` (in the gallery) are the same
    picture and would otherwise show twice on the article page.
    """
    stem = Path(name or '').stem.lower()
    return ROTATED_SUFFIX.sub('', SIZE_SUFFIX.sub('', stem))


class Command(BaseCommand):
    help = 'Import seed news/members JSON (with real scraped image URLs) into the database.'

    def handle(self, *args, **options):
        # Members/links are cheap (no per-item image downloads to wait on) and
        # matter for the homepage sidebar/members section, so seed them before
        # news, whose thumbnail/gallery downloads can take a long time and
        # must never block the rest of the seed from running.
        for step in (self.import_members, self.import_important_links, self.import_announcements, self.import_news):
            try:
                step()
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'{step.__name__} failed: {exc}'))

    def import_news(self):
        path = DATA_DIR / 'news.json'
        items = json.loads(path.read_text(encoding='utf-8'))
        created = 0
        for item in items:
            obj, _ = NewsItem.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'title': item['title'],
                    'title_en': item.get('title_en', ''),
                    'excerpt': item['excerpt'],
                    'excerpt_en': item.get('excerpt_en', ''),
                    'date': item['date'],
                    'content': item.get('content'),
                    'content_en': item.get('content_en', ''),
                },
            )
            if item.get('thumbnail') and not obj.thumbnail:
                try:
                    data = download(item['thumbnail'])
                    obj.thumbnail.save(filename_from_url(item['thumbnail']), ContentFile(data), save=True)
                except Exception as exc:
                    self.stderr.write(f"  thumbnail failed for {item['slug']}: {exc}")
            gallery = item.get('images') or []
            if gallery and not obj.images.exists():
                for order, url in enumerate(gallery):
                    try:
                        data = download(url)
                        img = NewsImage(news=obj, order=order)
                        img.image.save(filename_from_url(url), ContentFile(data), save=True)
                    except Exception as exc:
                        self.stderr.write(f"  gallery image failed for {item['slug']} ({url}): {exc}")
            created += 1

        removed = self.dedupe_gallery_photos()
        self.stdout.write(self.style.SUCCESS(
            f'Imported {created} news items ({removed} duplicate photos removed)'
        ))

    def dedupe_gallery_photos(self):
        """Drop gallery photos that repeat the thumbnail, or each other.

        Runs on every seed rather than only on first import: galleries are
        skipped once an item already has photos, so an environment seeded
        before the JSON was cleaned would otherwise keep its duplicates
        forever. Idempotent — a clean database loses nothing.
        """
        removed = 0
        for item in NewsItem.objects.all().prefetch_related('images'):
            seen = set()
            if item.thumbnail:
                seen.add(photo_key(item.thumbnail.name))
            for img in item.images.all():
                key = photo_key(img.image.name)
                if key in seen:
                    img.delete()
                    removed += 1
                else:
                    seen.add(key)
        return removed

    def import_announcements(self):
        path = DATA_DIR / 'announcements.json'
        if not path.exists():
            return
        items = json.loads(path.read_text(encoding='utf-8'))
        created = 0
        for index, item in enumerate(items):
            obj, _ = Announcement.objects.update_or_create(
                title=item['title'],
                defaults={
                    'title_en': item.get('title_en', ''),
                    'excerpt': item['excerpt'],
                    'excerpt_en': item.get('excerpt_en', ''),
                    'date': item.get('date'),
                    'link': item.get('link', ''),
                    'link_label': item.get('link_label', ''),
                    'link_label_en': item.get('link_label_en', ''),
                    'is_open': item.get('is_open', True),
                    'order': item.get('order', index),
                },
            )
            photo_url = item.get('photo')
            if photo_url and not obj.photo:
                try:
                    data = download(photo_url)
                    obj.photo.save(filename_from_url(photo_url), ContentFile(data), save=True)
                except Exception as exc:
                    self.stderr.write(f"  photo failed for {item['title']}: {exc}")
            links = item.get('links') or []
            if links and not obj.links.exists():
                for order, link_spec in enumerate(links):
                    try:
                        title_en = link_spec.get('title_en', '')
                        if link_spec.get('file_url'):
                            data = download(link_spec['file_url'])
                            doc = AnnouncementLink(
                                announcement=obj, title=link_spec['title'], title_en=title_en, order=order
                            )
                            doc.file.save(filename_from_url(link_spec['file_url']), ContentFile(data), save=True)
                        else:
                            AnnouncementLink.objects.create(
                                announcement=obj, title=link_spec['title'], title_en=title_en,
                                url=link_spec['url'], order=order,
                            )
                    except Exception as exc:
                        self.stderr.write(f"  link failed for {item['title']} ({link_spec.get('title')}): {exc}")
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {created} announcements'))

    def import_members(self):
        path = DATA_DIR / 'members.json'
        items = json.loads(path.read_text(encoding='utf-8'))
        created = 0
        for item in items:
            obj, _ = Member.objects.update_or_create(
                name=item['name'],
                defaults={'url': item['url']},
            )
            if item.get('logo') and not obj.logo:
                try:
                    data = download(item['logo'])
                    obj.logo.save(filename_from_url(item['logo']), ContentFile(data), save=True)
                except Exception as exc:
                    self.stderr.write(f"  logo failed for {item['name']}: {exc}")
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {created} members'))

    def import_important_links(self):
        path = DATA_DIR / 'important_links.json'
        if not path.exists():
            return
        items = json.loads(path.read_text(encoding='utf-8'))
        created = 0
        for item in items:
            ImportantLink.objects.update_or_create(
                title=item['title'],
                defaults={
                    'title_en': item.get('title_en', ''),
                    'url': item.get('url', ''),
                    'order': item.get('order', 0),
                },
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {created} important links'))
