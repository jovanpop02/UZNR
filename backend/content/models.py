from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone


def validate_link(value):
    """Accepts an external URL or a path to a file the site itself publishes.

    Plain URLField would reject "/documents/regulativa/zakon.pdf", and those
    paths are the whole point: most documents on this site are served by the
    frontend, not uploaded through the admin.
    """
    if not value or value.startswith('/'):
        return
    URLValidator(message='Unesite punu veb adresu (https://…) ili putanju koja počinje sa /.')(value)


class NewsItem(models.Model):
    slug = models.SlugField(unique=True, verbose_name='Link (slug)', help_text='Automatski se popunjava iz naslova. Koristi se u adresi stranice.')
    title = models.CharField(max_length=300, verbose_name='Naslov')
    title_en = models.CharField(max_length=300, blank=True, verbose_name='Naslov (EN)')
    excerpt = models.TextField(verbose_name='Kratak opis', help_text='Prikazuje se na početnoj stranici i u arhivi, ispod naslova.')
    excerpt_en = models.TextField(blank=True, verbose_name='Kratak opis (EN)')
    date = models.DateField(verbose_name='Datum objave')
    thumbnail = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='Naslovna fotografija', help_text='Glavna slika koja se prikazuje uz vijest.')
    content = models.TextField(blank=True, null=True, verbose_name='Tekst vijesti', help_text='Puni tekst koji se prikazuje na stranici vijesti.')
    content_en = models.TextField(blank=True, verbose_name='Tekst vijesti (EN)')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Vijest'
        verbose_name_plural = 'Vijesti'

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    news = models.ForeignKey(NewsItem, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_gallery/', verbose_name='Fotografija')
    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli.')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Fotografija'
        verbose_name_plural = 'Fotografije'

    def __str__(self):
        return f'Fotografija {self.order + 1}'


class ImportantLink(models.Model):
    title = models.CharField(max_length=200, verbose_name='Naziv')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='Naziv (EN)')
    url = models.URLField(blank=True, verbose_name='Veb adresa', help_text='Za link ka spoljnoj stranici (npr. sajt ministarstva).')
    file = models.FileField(upload_to='important_links/', blank=True, verbose_name='Fajl', help_text='Za dokument koji se otprema i čuva na našem sajtu (PDF i sl.). Popuni ili ovo, ili adresu iznad — ne oboje.')
    logo = models.ImageField(upload_to='important_links_logos/', blank=True, null=True, verbose_name='Logo', help_text='Logo institucije koji se prikazuje uz link.')
    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli.')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Važan link'
        verbose_name_plural = 'Važni linkovi'

    def clean(self):
        if not self.url and not self.file:
            raise ValidationError('Unesite veb adresu ili otpremite fajl.')
        if self.url and self.file:
            raise ValidationError('Popunite samo jedno: veb adresu ili fajl, ne oboje.')

    def __str__(self):
        return self.title


class Announcement(models.Model):
    title = models.CharField(max_length=300, verbose_name='Naslov')
    title_en = models.CharField(max_length=300, blank=True, verbose_name='Naslov (EN)')
    excerpt = models.TextField(verbose_name='Tekst oglasa')
    excerpt_en = models.TextField(blank=True, verbose_name='Tekst oglasa (EN)')
    date = models.DateField(blank=True, null=True, verbose_name='Datum objave', help_text='Ostavi prazno ako datum nije poznat — oglas će se prikazati bez datuma.')
    photo = models.ImageField(upload_to='oglasi/', blank=True, null=True, verbose_name='Fotografija')
    link = models.URLField(blank=True, verbose_name='Link', help_text='Opciono — npr. link za prijavu ili više informacija.')
    link_label = models.CharField(max_length=100, blank=True, verbose_name='Tekst linka', help_text='Npr. "Prijava putem portala eUprava". Ostavi prazno za podrazumijevani tekst.')
    link_label_en = models.CharField(max_length=100, blank=True, verbose_name='Tekst linka (EN)')
    is_open = models.BooleanField(default=True, verbose_name='Aktivan (otvoren)', help_text='Isključi kada rok istekne ili se pozicija popuni — oglas ostaje na sajtu, ali se označava kao "Isteklo".')
    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli. Prvi oglas se prikazuje istaknuto, u većoj kartici.')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Oglas'
        verbose_name_plural = 'Oglasi'

    def __str__(self):
        return self.title


class AnnouncementLink(models.Model):
    announcement = models.ForeignKey(Announcement, related_name='links', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Naziv')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='Naziv (EN)')
    url = models.URLField(blank=True, verbose_name='Veb adresa', help_text='Za link ka spoljnoj stranici.')
    file = models.FileField(upload_to='oglasi_dokumenti/', blank=True, verbose_name='Fajl', help_text='Za dokument koji se otprema i čuva na našem sajtu (PDF i sl.). Popuni ili ovo, ili adresu iznad — ne oboje.')
    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli.')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Dokument uz oglas'
        verbose_name_plural = 'Dokumenti uz oglas'

    def clean(self):
        if not self.url and not self.file:
            raise ValidationError('Unesite veb adresu ili otpremite fajl.')
        if self.url and self.file:
            raise ValidationError('Popunite samo jedno: veb adresu ili fajl, ne oboje.')

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """A message sent from the contact form on /kontakt.

    Deliberately stores no IP address or user agent: the consent checkbox on the
    form promises the data is used only to reply, and abuse is handled by
    request throttling rather than by keeping identifiers on file.
    """

    class Status(models.TextChoices):
        NEW = 'new', 'Novo'
        IN_PROGRESS = 'in_progress', 'U obradi'
        ANSWERED = 'answered', 'Odgovoreno'

    name = models.CharField(max_length=200, verbose_name='Ime i prezime')
    email = models.EmailField(verbose_name='E-mail')
    subject = models.CharField(max_length=200, verbose_name='Naslov')
    message = models.TextField(verbose_name='Poruka')
    language = models.CharField(
        max_length=5,
        default='mne',
        verbose_name='Jezik',
        help_text='Jezik sajta na kojem je poruka poslata — potvrda se šalje na tom jeziku.',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Primljeno')
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW, verbose_name='Status'
    )
    notes = models.TextField(blank=True, verbose_name='Interna bilješka', help_text='Vidljivo samo u administraciji.')
    confirmation_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Potvrda poslata',
        help_text='Vrijeme slanja automatske potvrde pošiljaocu. Prazno znači da slanje nije uspjelo.',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Poruka sa sajta'
        verbose_name_plural = 'Poruke sa sajta'

    def __str__(self):
        return f'{self.name} — {self.subject}'

    def mark_confirmation_sent(self):
        self.confirmation_sent_at = timezone.now()
        self.save(update_fields=['confirmation_sent_at'])


class Page(models.Model):
    """One page of the site whose content staff can edit.

    The page's layout stays in the frontend; what lives here is the content it
    renders — headings, paragraphs, links, documents and images, grouped into
    sections. Every text field is stored twice, Montenegrin and English, and the
    API falls back to Montenegrin wherever the English is left blank.
    """

    slug = models.SlugField(
        unique=True,
        verbose_name='Adresa stranice (slug)',
        help_text='Mora odgovarati adresi na sajtu, npr. "regulativa" za /regulativa.',
    )
    title = models.CharField(max_length=200, verbose_name='Naslov')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='Naslov (EN)')
    intro = models.TextField(blank=True, verbose_name='Uvodni tekst')
    intro_en = models.TextField(blank=True, verbose_name='Uvodni tekst (EN)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Izmijenjeno')

    class Meta:
        ordering = ['slug']
        verbose_name = 'Stranica'
        verbose_name_plural = 'Stranice'

    def __str__(self):
        return self.title


class PageSection(models.Model):
    """A block within a page: a run of text, or a list of links/documents/images."""

    class Kind(models.TextChoices):
        TEXT = 'text', 'Tekst'
        LINKS = 'links', 'Linkovi'
        DOCUMENTS = 'documents', 'Dokumenti'
        IMAGES = 'images', 'Galerija fotografija'
        FAQ = 'faq', 'Pitanja i odgovori'

    page = models.ForeignKey(Page, related_name='sections', on_delete=models.CASCADE, verbose_name='Stranica')
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        default=Kind.TEXT,
        verbose_name='Tip sekcije',
        help_text='Određuje kako se sekcija prikazuje na sajtu. "Tekst" koristi samo polja ispod; ostali tipovi koriste i stavke.',
    )
    heading = models.CharField(max_length=200, blank=True, verbose_name='Naslov sekcije')
    heading_en = models.CharField(max_length=200, blank=True, verbose_name='Naslov sekcije (EN)')
    body = models.TextField(
        blank=True,
        verbose_name='Tekst',
        help_text='Prazan red razdvaja pasuse.',
    )
    body_en = models.TextField(blank=True, verbose_name='Tekst (EN)')
    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli.')
    is_visible = models.BooleanField(
        default=True,
        verbose_name='Prikazano',
        help_text='Isključi da sekcija privremeno nestane sa sajta bez brisanja.',
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Sekcija'
        verbose_name_plural = 'Sekcije'

    def __str__(self):
        return self.heading or self.get_kind_display()


class PageContentProxy(PageSection):
    """Base for the one-entry-per-site-page views in the admin.

    The admin home page used to carry a single "Stranice" entry, and finding
    Regulativa meant knowing it was a Page, opening a list, then opening its
    sections. Each site page now gets its own entry instead, and clicking it
    lands directly on that page's sections.

    Every subclass is a proxy of PageSection — same table, no migration of data,
    only a different label and a filtered queryset. `page_slug` names the page a
    subclass belongs to; the admin uses it both to filter the list and to fill
    in the page on newly added sections.
    """

    page_slug = None

    class Meta:
        proxy = True
        verbose_name = 'sekcija'
        verbose_name_plural = 'sekcije'


class RegulativaPage(PageContentProxy):
    """Regulativa is the one page that genuinely needs the block layer.

    Its ~50 documents are split into seven thematic groups that render as
    subheadings on the site, so the blocks are content, not scaffolding. Every
    other page holds a single block, and for those the layer is skipped — see
    the SectionItem proxies below.
    """

    page_slug = 'regulativa'

    class Meta:
        proxy = True
        verbose_name = 'grupa na stranici Regulativa'
        verbose_name_plural = 'Regulativa'


class ProjektiPage(PageContentProxy):
    """Grouped, not flat: each project is a block and its documents are the
    items inside it. One project carries 87 files, which a single item could
    never hold."""

    page_slug = 'projekti'

    class Meta:
        proxy = True
        verbose_name = 'projekat'
        verbose_name_plural = 'Projekti'


class BibliotekaPage(PageContentProxy):
    """Grouped for the same reason: the library is a few themed shelves
    (stručni ispit, EU-OSHA kampanje) rather than one long list."""

    page_slug = 'biblioteka'

    class Meta:
        proxy = True
        verbose_name = 'grupa u Biblioteci'
        verbose_name_plural = 'Biblioteka'


class SectionItem(models.Model):
    """One entry inside a section — a link, a document, an image or a Q&A pair."""

    section = models.ForeignKey(PageSection, related_name='items', on_delete=models.CASCADE, verbose_name='Sekcija')
    title = models.CharField(max_length=300, verbose_name='Naziv')
    title_en = models.CharField(max_length=300, blank=True, verbose_name='Naziv (EN)')
    description = models.TextField(blank=True, verbose_name='Opis')
    description_en = models.TextField(blank=True, verbose_name='Opis (EN)')
    url = models.CharField(
        max_length=500,
        blank=True,
        validators=[validate_link],
        verbose_name='Veb adresa',
        help_text='Puna adresa (https://…) za spoljnu stranicu, ili putanja do dokumenta '
                  'koji je već na sajtu (npr. /documents/regulativa/zakon.pdf).',
    )
    file = models.FileField(
        upload_to='stranice/dokumenti/',
        blank=True,
        verbose_name='Fajl',
        help_text='Za dokument koji se čuva na našem sajtu (PDF i sl.). Popuni ili ovo, ili adresu iznad — ne oboje.',
    )
    image = models.ImageField(upload_to='stranice/slike/', blank=True, null=True, verbose_name='Fotografija')
    image_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Adresa fotografije',
        help_text='Koristi se samo kada fotografija već postoji na sajtu (npr. /press/slika.jpg). '
                  'Ako otpremite fotografiju iznad, ona ima prednost.',
    )

    # Small print under a document or press item. All optional — a plain link
    # leaves them empty.
    reference = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Izvor / broj službenog lista',
        help_text='Npr. „Službeni list Crne Gore“, br. 051/26 — ili naziv medija za press objave.',
    )
    reference_en = models.CharField(max_length=300, blank=True, verbose_name='Izvor (EN)')
    date_label = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='Datum (tekst)',
        help_text='Prikazuje se kako je unijet, npr. 20.03.2026.',
    )
    pages = models.PositiveIntegerField(blank=True, null=True, verbose_name='Broj strana')
    size_kb = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Veličina (KB)',
        help_text='Popunjava se automatski pri otpremanju fajla.',
    )

    order = models.PositiveIntegerField(default=0, verbose_name='Redoslijed', help_text='Postavlja se prevlačenjem reda u tabeli.')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Stavka'
        verbose_name_plural = 'Stavke'

    def clean(self):
        if self.url and self.file:
            raise ValidationError('Popunite samo jedno: veb adresu ili fajl, ne oboje.')
        kind = self.section.kind if self.section_id else None
        if kind in (PageSection.Kind.LINKS, PageSection.Kind.DOCUMENTS) and not (self.url or self.file):
            raise ValidationError('Unesite veb adresu ili otpremite fajl.')
        if kind == PageSection.Kind.IMAGES and not self.image:
            raise ValidationError('Otpremite fotografiju.')

    def save(self, *args, **kwargs):
        # Staff should not have to look up a file's size by hand; the size is
        # shown on the document cards, so fill it in from the upload itself.
        if self.file and not self.size_kb:
            try:
                self.size_kb = max(1, round(self.file.size / 1024))
            except (OSError, ValueError):
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SinglePageContent(SectionItem):
    """A page whose whole content is one flat list, edited without the block layer.

    Most pages hold exactly one block, so making someone open the page, then
    open its only block, then edit the list inside it is two clicks and one
    concept more than the job needs. These proxies bind straight to the items:
    the admin entry *is* the list of documents, links or questions, and the
    block it belongs to is created and maintained behind the scenes.

    `page_slug` names the page. Regulativa is deliberately not in this family —
    its blocks are real subheadings on the site.
    """

    page_slug = None

    class Meta:
        proxy = True
        verbose_name = 'stavka'
        verbose_name_plural = 'stavke'


class PublikacijePage(SinglePageContent):
    page_slug = 'publikacije'

    class Meta:
        proxy = True
        verbose_name = 'publikacija'
        verbose_name_plural = 'Publikacije'


class PressPage(SinglePageContent):
    page_slug = 'press'

    class Meta:
        proxy = True
        verbose_name = 'objava u medijima'
        verbose_name_plural = 'Press / Mediji'


class PitanjaPage(SinglePageContent):
    page_slug = 'pitanja-odgovori'

    class Meta:
        proxy = True
        verbose_name = 'pitanje'
        verbose_name_plural = 'Pitanja i odgovori'


class Member(models.Model):
    name = models.CharField(max_length=200, verbose_name='Naziv')
    url = models.URLField(verbose_name='Veb adresa')
    logo = models.ImageField(upload_to='members/', blank=True, null=True, verbose_name='Logo')

    class Meta:
        ordering = ['name']
        verbose_name = 'Član'
        verbose_name_plural = 'Članovi'

    def __str__(self):
        return self.name
