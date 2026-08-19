"""The editing interface staff use to run the site.

Three conventions hold throughout, and they are what keep this admin legible to
someone who does not know Django:

  * Every registered model carries a ``description`` — one sentence saying what
    it is and which page of the public site it feeds. It is printed on the admin
    home page and again above each list, so the answer to "what am I editing and
    where does it show up?" is always on screen.
  * Only the six things staff actually manage appear on the home page. Sections
    and items are parts of a page, not separate things to manage, so they are
    reached by opening the page that contains them.
  * Colour and shape live in ``custom_admin.css``. Nothing here writes inline
    styles; badges emit a class name and the stylesheet decides how it looks,
    which is also what lets the badges follow the admin's light and dark themes.
"""

import json

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .emails import send_confirmation
from .models import (
    Announcement,
    AnnouncementLink,
    BibliotekaPage,
    ContactMessage,
    ImportantLink,
    Member,
    NewsImage,
    NewsItem,
    Page,
    PageSection,
    PitanjaPage,
    PressPage,
    ProjektiPage,
    PublikacijePage,
    RegulativaPage,
    SectionItem,
)

# The home page groups the content models under plain-language headings rather
# than listing all eleven in one run. The grouping answers "what am I here to
# do" -- publish something, edit a page, change what shows on the home page,
# read the inbox -- instead of making staff scan a flat list every visit.
#
# Each entry is (heading, blurb, [object names in display order]). Anything not
# named here still renders, under HOME_GROUP_OTHER.
HOME_GROUPS = [
    (
        'Sadržaj sajta',
        'Tekst, dokumenti i objave koje sajt prikazuje.',
        [
            'NewsItem',
            'Announcement',
            'RegulativaPage',
            'ProjektiPage',
            'PublikacijePage',
            'BibliotekaPage',
            'PressPage',
            'PitanjaPage',
        ],
    ),
    (
        'Početna strana',
        'Ono što se prikazuje na naslovnoj strani sajta.',
        ['ImportantLink', 'Member'],
    ),
]

HOME_GROUP_OTHER = ('Ostalo', '', [])

# Vijesti and oglasi are edited far more often than the page content they sit
# beside, so they share the section but not the weight: app_list.html gives
# these two a heavier card.
HOME_FEATURED = {'NewsItem', 'Announcement'}

# The inbox is reachable from the header on every page, so a card for it on the
# home page would be a second door to the same room.
HOME_HIDDEN = {'ContactMessage'}

# The home page lists models in this order rather than alphabetically, so the
# things edited daily come first and the inbox sits at the bottom. Anything not
# named here falls to the end.
HOME_ORDER = [
    'NewsItem',
    'RegulativaPage',
    'ProjektiPage',
    'Announcement',
    'PublikacijePage',
    'BibliotekaPage',
    'PressPage',
    'PitanjaPage',
    'ImportantLink',
    'Member',
    'ContactMessage',
]

# Printed on every form that pairs a Montenegrin field with its English twin.
EN_NOTE = (
    'Engleski je desno od crnogorskog. Ako ga ostavite prazan, na '
    'engleskom sajtu se prikazuje crnogorski tekst.'
)

_django_get_app_list = admin.AdminSite.get_app_list


def _get_app_list(self, request, app_label=None):
    """Order the home page by HOME_ORDER and carry each model's description.

    The description lives on the ModelAdmin, but the home page renders from
    plain dicts built by Django, so it has to be copied across here for
    ``app_list.html`` to be able to print it.
    """
    app_list = _django_get_app_list(self, request, app_label)

    for app in app_list:
        for entry in app['models']:
            model_admin = self._registry.get(entry.get('model'))
            entry['description'] = getattr(model_admin, 'description', '')
            entry['count'] = _model_count(model_admin, request)
            entry['featured'] = entry.get('object_name') in HOME_FEATURED
            # Unanswered messages are the one thing here with a clock on it.
            # Everything else waits patiently; a visitor who wrote in does not.
            entry['badge'] = ''
            entry['urgent'] = False
            if entry.get('object_name') == 'ContactMessage':
                waiting = ContactMessage.objects.filter(
                    status=ContactMessage.Status.NEW
                ).count()
                if waiting:
                    entry['badge'] = (
                        f'{waiting} novih' if waiting != 1 else '1 nova'
                    )
                    entry['urgent'] = True
        app['models'].sort(
            key=lambda entry: (
                HOME_ORDER.index(entry['object_name'])
                if entry['object_name'] in HOME_ORDER
                else len(HOME_ORDER)
            )
        )

        # Bucket the models for the dashboard's grouped card layout. The plain
        # `models` list is left untouched: the collapsible sidebar renders from
        # the same template and wants the flat version.
        if app.get('app_label') == 'content':
            app['groups'] = _grouped(app['models'])
        else:
            # Django's own apps (just auth, for "Korisnici") are not part of the
            # site's content. The dashboard links to them from its left rail
            # instead of giving them a card; `groups` stays empty so
            # app_list.html skips the app there. The sidebar still lists them,
            # because it renders from `models`.
            app['groups'] = []

    # Content first, Django's own auth app after it. "Korisnici" is account
    # plumbing rather than something anyone comes here to edit, so it should
    # not be the first thing on the page.
    app_list.sort(key=lambda app: 0 if app.get('app_label') == 'content' else 1)

    return app_list


def _model_count(model_admin, request):
    """Row count for a model's card, or None when it cannot be determined.

    Counts go through the ModelAdmin's own queryset rather than the bare
    manager, so the proxy models that carve one table into several admin
    entries (Regulativa, Projekti, Biblioteka...) each report their own slice
    instead of the whole table.
    """
    if model_admin is None:
        return None
    try:
        return model_admin.get_queryset(request).count()
    except Exception:
        # A card without a number is a smaller loss than a dashboard that
        # will not render, so a misbehaving queryset is not fatal here.
        return None


def _grouped(models):
    """Split a model list into the HOME_GROUPS buckets, dropping empty ones."""
    models = [e for e in models if e['object_name'] not in HOME_HIDDEN]
    by_name = {entry['object_name']: entry for entry in models}
    used = set()
    groups = []

    for title, blurb, names in HOME_GROUPS:
        picked = [by_name[name] for name in names if name in by_name]
        if not picked:
            continue
        used.update(entry['object_name'] for entry in picked)
        groups.append({'title': title, 'blurb': blurb, 'models': picked})

    leftover = [e for e in models if e['object_name'] not in used]
    if leftover:
        title, blurb, _ = HOME_GROUP_OTHER
        groups.append({'title': title, 'blurb': blurb, 'models': leftover})

    return groups


admin.AdminSite.get_app_list = _get_app_list

# Bulk delete is off everywhere. Deleting a row is a deliberate act done from
# that row's own page, where you can see what you are about to lose; a dropdown
# that wipes out everything currently ticked is the one action in this admin
# that cannot be undone by retyping something.
admin.site.disable_action('delete_selected')

# Groups are Django's permission machinery. This site has one kind of staff
# member, so the entry only adds a box nobody should open. Users stay listed —
# that is how a new colleague gets an account.
admin.site.unregister(Group)


class RowDeleteMixin:
    """Adds a delete link to each row of a list.

    Bulk delete is off on purpose — a dropdown that wipes out whatever is ticked
    is the one thing here nobody can undo. But that left deleting a single row
    as a four-step trip: open it, scroll past every field, press Obriši, then
    confirm. The link below skips straight to Django's confirmation page, which
    is the step that actually protects anything: it names the object and lists
    what else would go with it.
    """

    def get_list_display(self, request):
        """Drop the column for anyone who may not delete.

        Display methods never see the request, so the check has to happen here.
        Leaving the link visible to a read-only account would offer an action
        that only ends in a permission error.
        """
        columns = super().get_list_display(request)
        if self.has_delete_permission(request):
            return columns
        return tuple(column for column in columns if column != 'delete_link')

    @admin.display(description='')
    def delete_link(self, obj):
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_delete',
            args=[obj.pk],
        )
        return format_html('<a class="row-delete" href="{}" title="Obriši">Obriši</a>', url)


class SiteLinkMixin:
    """Adds a link that opens the edited thing on the public site.

    Checking a change used to mean remembering the address and typing it in.
    `site_path` is either a plain path or a callable taking the object, so a
    news item can point at its own page while a link points at the home page
    section it appears in.
    """

    site_path = None

    @admin.display(description='')
    def site_link(self, obj):
        path = self.site_path(obj) if callable(self.site_path) else self.site_path
        if not path:
            return ''
        return format_html(
            '<a class="site-link" href="{}{}" target="_blank" rel="noopener" '
            'title="Otvara se na sajtu, u novoj kartici">Pogledaj</a>',
            settings.SITE_URL.rstrip('/'), path,
        )


class DragOrderedAdmin(SiteLinkMixin, RowDeleteMixin, admin.ModelAdmin):
    """Changelist whose rows are ordered by dragging them.

    There is no order column and no handle: the row itself is what you grab.
    Dropping it renumbers every row from the top and saves immediately, so the
    number nobody wanted to think about stays an implementation detail.

    Dragging is only offered while the list is in its stored order. Sorting by
    another column and then dragging would be meaningless — the new positions
    would describe a sequence the visitor never sees — so in that case the rows
    are inert and the page says why.
    """

    reorder_field = 'order'

    # reorder.js is loaded for the whole admin from base_site.html, because the
    # inline tables it also drives appear on pages this ModelAdmin never serves.

    def get_urls(self):
        return [
            path(
                'reorder/',
                self.admin_site.admin_view(self.reorder_view),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_reorder',
            ),
            *super().get_urls(),
        ]

    def reorder_view(self, request):
        """Persist a new order posted by the drag script."""
        if request.method != 'POST':
            return HttpResponseBadRequest('POST required')
        if not self.has_change_permission(request):
            return JsonResponse({'error': 'forbidden'}, status=403)

        try:
            ids = json.loads(request.body)['ids']
            ids = [int(pk) for pk in ids]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return HttpResponseBadRequest('expected {"ids": [...]}')

        objects = self.model._default_manager.in_bulk(ids)
        if len(objects) != len(ids):
            return HttpResponseBadRequest('unknown id')

        # One UPDATE per row, but in a single transaction: a half-applied order
        # would leave the page in a sequence nobody chose.
        with transaction.atomic():
            for position, pk in enumerate(ids):
                row = objects[pk]
                setattr(row, self.reorder_field, position)
                row.save(update_fields=[self.reorder_field])

        return JsonResponse({'status': 'ok', 'count': len(ids)})


class ReorderableInline(admin.TabularInline):
    """Inline whose rows are ordered by dragging them.

    The `order` field has to stay on the form — it is what actually gets saved —
    but it is rendered as a hidden input rather than a number box. Django marks
    both the column header and its cells `hidden` when a widget is hidden, so
    the "Redoslijed" column disappears through Django's own mechanism instead of
    being covered up by a stylesheet rule.

    The script finds these tables by the `reorderable` class and rewrites the
    hidden inputs when a row is dropped.
    """

    classes = ('reorderable',)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'order':
            kwargs['widget'] = forms.HiddenInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class NewsImageInline(ReorderableInline):
    model = NewsImage
    extra = 1
    fields = ('preview', 'image', 'order')
    readonly_fields = ('preview',)
    classes = ('news-gallery-inline', 'reorderable', 'collapse')
    verbose_name = 'Fotografija'
    verbose_name_plural = 'Fotografije — prevucite da promijenite redoslijed'

    @admin.display(description='')
    def preview(self, obj):
        if not obj.pk or not obj.image:
            return ''
        return format_html(
            '<img src="{}" class="gallery-thumb" alt="" />', obj.image.url
        )


@admin.register(NewsItem)
class NewsItemAdmin(SiteLinkMixin, RowDeleteMixin, admin.ModelAdmin):
    description = (
        'Vijesti i objave Udruženja. Najnovije se prikazuju na početnoj strani, '
        'sve zajedno u Arhivi, a svaka ima i svoju stranicu (/vijesti/…).'
    )

    list_display = ('thumb', 'title', 'date', 'site_link', 'delete_link')
    site_path = staticmethod(lambda obj: f'/vijesti/{obj.slug}')
    list_display_links = ('thumb', 'title')
    list_filter = ('date',)
    search_fields = ('title', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-date',)
    actions = None
    inlines = [NewsImageInline]

    fieldsets = (
        ('Vijest', {
            'fields': (('title', 'title_en'), 'date', 'thumbnail'),
            'description': 'Naslov, datum objave i glavna fotografija. '
                           'Engleski je desno; ako ga ostavite prazan, na engleskom '
                           'sajtu se prikazuje crnogorski tekst.',
        }),
        ('Tekst', {
            'fields': (('excerpt', 'excerpt_en'), ('content', 'content_en')),
            'description': 'Kratak opis se vidi na početnoj strani i u arhivi. '
                           'Puni tekst se vidi kada se vijest otvori.',
        }),
        ('Tehnički podaci', {
            'fields': ('slug',),
            'classes': ('collapse',),
            'description': 'Adresa vijesti na sajtu. Popunjava se sama iz naslova.',
        }),
    )

    @admin.display(description='')
    def thumb(self, obj):
        if not obj.thumbnail:
            return '—'
        return format_html('<img src="{}" class="list-thumb" alt="" />', obj.thumbnail.url)


class AnnouncementLinkInline(ReorderableInline):
    model = AnnouncementLink
    extra = 1
    fields = ('title', 'title_en', 'url', 'file', 'order')
    verbose_name = 'Dokument uz oglas'
    verbose_name_plural = 'Dokumenti uz oglas — prevucite da promijenite redoslijed'


@admin.register(Announcement)
class AnnouncementAdmin(DragOrderedAdmin):
    description = (
        'Konkursi, pozivi i oglasi. Prikazuju se na stranici Oglasi i u Arhivi. '
        'Oglas sa najmanjim redoslijedom prikazuje se istaknuto, u većoj kartici.'
    )

    list_display = ('thumb', 'title', 'status', 'date', 'site_link', 'delete_link')
    site_path = '/oglasi'
    list_display_links = ('thumb', 'title')
    list_filter = ('is_open', 'date')
    search_fields = ('title', 'excerpt')
    ordering = ('order', 'id')
    actions = None
    inlines = [AnnouncementLinkInline]

    fieldsets = (
        ('Oglas', {
            'fields': (('title', 'title_en'), 'date', 'is_open'),
            'description': 'Isključite „Aktivan“ kada rok istekne — oglas ostaje '
                           'na sajtu, ali se označava kao isteklo. Engleski je desno; '
                           'prazan znači da se prikazuje crnogorski.',
        }),
        ('Tekst i fotografija', {
            'fields': (('excerpt', 'excerpt_en'), 'photo'),
        }),
        ('Link u tekstu', {
            'fields': ('link', ('link_label', 'link_label_en')),
            'classes': ('collapse',),
            'description': 'Opciono. Pretvara jednu riječ u tekstu oglasa u link '
                           '(npr. „eUprava“).',
        }),
    )

    @admin.display(description='')
    def thumb(self, obj):
        if not obj.photo:
            return '—'
        return format_html('<img src="{}" class="list-thumb" alt="" />', obj.photo.url)

    @admin.display(description='Status', ordering='is_open')
    def status(self, obj):
        if obj.is_open:
            return mark_safe('<span class="badge badge--open">Otvoreno</span>')
        return mark_safe('<span class="badge badge--muted">Isteklo</span>')


@admin.register(ImportantLink)
class ImportantLinkAdmin(DragOrderedAdmin):
    description = (
        'Linkovi ka institucijama i korisni dokumenti. Prikazuju se u sekciji '
        '„Važni linkovi“ na početnoj strani.'
    )

    list_display = ('logo_thumb', 'title', 'destination', 'site_link', 'delete_link')
    search_fields = ('title', 'title_en')
    site_path = '/'
    list_display_links = ('title',)
    ordering = ('order', 'id')
    actions = None

    fieldsets = (
        (None, {
            'fields': (('title', 'title_en'), 'logo'),
            'description': 'Naziv institucije ili dokumenta. ' + EN_NOTE,
        }),
        ('Gdje vodi', {
            'fields': ('url', 'file'),
            'description': 'Popunite samo jedno — spoljnu adresu ili fajl.',
        }),
    )

    @admin.display(description='')
    def logo_thumb(self, obj):
        if not obj.logo:
            return '—'
        return format_html('<img src="{}" class="list-thumb list-thumb--logo" alt="" />', obj.logo.url)

    @admin.display(description='Vodi na')
    def destination(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Fajl ↗</a>', obj.file.url)
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
        return '—'


@admin.register(Member)
class MemberAdmin(SiteLinkMixin, RowDeleteMixin, admin.ModelAdmin):
    description = (
        'Organizacije članice Udruženja. Prikazuju se sa logotipom u sekciji '
        '„Članovi“ na početnoj strani.'
    )

    list_display = ('logo_thumb', 'name', 'url', 'site_link', 'delete_link')
    site_path = '/'
    list_display_links = ('logo_thumb', 'name')
    search_fields = ('name',)
    ordering = ('name',)
    actions = None

    @admin.display(description='')
    def logo_thumb(self, obj):
        if not obj.logo:
            return '—'
        return format_html('<img src="{}" class="list-thumb list-thumb--logo" alt="" />', obj.logo.url)


@admin.register(ContactMessage)
class ContactMessageAdmin(RowDeleteMixin, admin.ModelAdmin):
    """Inbox for the contact form.

    Messages arrive from the website, so the admin cannot create them and the
    submitted fields are read-only — an inbox nobody can rewrite. Only the two
    fields staff own, status and the internal note, stay editable.
    """

    description = (
        'Poruke poslate preko forme na stranici Kontakt. Ovo je interno sanduče — '
        'poruke se ne prikazuju na sajtu i ne mogu se dodavati ručno.'
    )

    list_display = ('created', 'name', 'subject_label', 'email', 'status_badge', 'confirmation', 'delete_link')
    list_display_links = ('created', 'name')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = ('mark_answered', 'mark_in_progress', 'resend_confirmation')

    readonly_fields = (
        'name', 'email', 'subject', 'message',
        'language', 'created_at', 'confirmation_sent_at',
    )

    fieldsets = (
        ('Poruka', {
            'fields': ('name', 'email', 'subject', 'message'),
        }),
        ('Obrada', {
            'fields': ('status', 'notes'),
            'description': 'Jedina polja koja se mogu mijenjati — sadržaj poruke se ne uređuje.',
        }),
        ('Detalji', {
            'fields': ('created_at', 'language', 'confirmation_sent_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Primljeno', ordering='created_at')
    def created(self, obj):
        return obj.created_at.strftime('%d.%m.%Y. %H:%M')

    @admin.display(description='Naslov', ordering='subject')
    def subject_label(self, obj):
        return obj.subject

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        modifiers = {
            ContactMessage.Status.NEW: 'new',
            ContactMessage.Status.IN_PROGRESS: 'progress',
            ContactMessage.Status.ANSWERED: 'done',
        }
        return format_html(
            '<span class="badge badge--{}">{}</span>',
            modifiers.get(obj.status, 'muted'),
            obj.get_status_display(),
        )

    @admin.display(description='Potvrda', ordering='confirmation_sent_at')
    def confirmation(self, obj):
        if obj.confirmation_sent_at:
            return format_html(
                '<span class="badge badge--done" title="{}">Poslata</span>',
                obj.confirmation_sent_at.strftime('%d.%m.%Y. %H:%M'),
            )
        return mark_safe('<span class="badge badge--fail">Nije poslata</span>')

    @admin.action(description='Označi kao odgovoreno')
    def mark_answered(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.ANSWERED)
        self.message_user(request, f'Označeno kao odgovoreno: {updated}.', messages.SUCCESS)

    @admin.action(description='Označi kao u obradi')
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.IN_PROGRESS)
        self.message_user(request, f'Označeno kao u obradi: {updated}.', messages.SUCCESS)

    @admin.action(description='Ponovo pošalji potvrdu pošiljaocu')
    def resend_confirmation(self, request, queryset):
        sent = sum(1 for message in queryset if send_confirmation(message))
        failed = queryset.count() - sent
        if sent:
            self.message_user(request, f'Potvrda ponovo poslata: {sent}.', messages.SUCCESS)
        if failed:
            self.message_user(
                request,
                f'Slanje nije uspjelo za {failed} poruka — provjerite podešavanja mejla.',
                messages.ERROR,
            )


class SectionItemInline(ReorderableInline):
    """Compact list of a section's items.

    Tabular rather than stacked because a section can hold fifty documents, and
    stacked inlines turn that into a page metres long. The fields here are the
    ones staff change routinely; the rest (photo, English text, page count) are
    on the item's own edit page behind the pencil.
    """

    model = SectionItem
    extra = 1
    fields = ('title', 'title_en', 'url', 'file', 'reference', 'order')
    ordering = ('order', 'id')
    show_change_link = True
    verbose_name = 'Stavka'
    verbose_name_plural = (
        'Stavke (linkovi, dokumenti, fotografije) — prevucite da promijenite '
        'redoslijed, olovkom otvorite ostala polja'
    )

    # Default admin text inputs are wide enough to push the last column off the
    # screen in a five-column inline.
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '28'})},
    }


@admin.register(SectionItem)
class SectionItemAdmin(RowDeleteMixin, admin.ModelAdmin):
    """Full editor for a single item, including both languages and the photo."""

    description = (
        'Pojedinačna stavka unutar sekcije — dokument, link, fotografija ili '
        'pitanje. Otvara se olovkom iz sekcije kojoj pripada.'
    )

    list_display = ('title', 'section', 'page', 'destination', 'delete_link')
    list_display_links = ('title',)
    list_filter = ('section__page', 'section')
    search_fields = ('title', 'title_en', 'reference')
    ordering = ('section', 'order', 'id')
    actions = None

    fieldsets = (
        (None, {
            'fields': (('title', 'title_en'), ('description', 'description_en')),
            'description': 'Naziv koji se vidi na sajtu i, ako treba, kratak opis '
                           'ispod njega. ' + EN_NOTE,
        }),
        ('Gdje vodi', {
            'fields': ('url', 'file'),
            'description': 'Popunite samo jedno — spoljnu adresu ili fajl.',
        }),
        ('Dodatni podaci', {
            'fields': (('reference', 'reference_en'), 'date_label', 'pages', 'size_kb'),
            'classes': ('collapse',),
            'description': 'Sitni tekst ispod naziva — broj službenog lista, izvor, datum, broj strana.',
        }),
        ('Fotografija', {
            'fields': ('image', 'image_url'),
            'classes': ('collapse',),
        }),
    )

    def get_model_perms(self, request):
        """Keep this off the home page.

        A stavka is part of a section, which is part of a page — it is edited by
        opening the page that contains it, never picked from a list of every
        item on the site. Returning no perms hides the entry from the home page
        while leaving the edit pages themselves reachable, which is what the
        pencil in the section inline links to.
        """
        return {}

    @admin.display(description='Stranica')
    def page(self, obj):
        return obj.section.page

    @admin.display(description='Vodi na')
    def destination(self, obj):
        target = obj.file.url if obj.file else obj.url
        if not target:
            return '—'
        return format_html('<a href="{}" target="_blank">{}</a>', target, target[:60])


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    """Sections are edited on their own page, because that is the only place the
    items inside them can be edited too — Django cannot nest an inline inside an
    inline."""

    description = (
        'Jedan blok unutar stranice — tekst, spisak linkova, dokumenata, '
        'fotografija ili pitanja. Otvara se iz stranice kojoj pripada.'
    )

    list_display = ('heading_display', 'page', 'kind', 'item_count', 'is_visible')
    list_display_links = ('heading_display',)
    list_filter = ('page', 'kind', 'is_visible')
    ordering = ('page', 'order', 'id')
    actions = None
    inlines = [SectionItemInline]

    fieldsets = (
        (None, {
            'fields': ('page', 'kind', 'is_visible'),
        }),
        ('Naslov sekcije', {
            'fields': ('heading', 'heading_en'),
        }),
        ('Tekst', {
            'fields': ('body', 'body_en'),
            'description': 'Prazan red razdvaja pasuse. Za sekcije sa linkovima ili dokumentima ovo je uvodni tekst i može ostati prazno.',
        }),
    )

    def get_model_perms(self, request):
        """Hidden from the home page for the same reason as SectionItem: a
        section belongs to a page and is opened from it."""
        return {}

    @admin.display(description='Sekcija')
    def heading_display(self, obj):
        return obj.heading or f'({obj.get_kind_display()})'

    @admin.display(description='Stavki')
    def item_count(self, obj):
        return obj.items.count()


class PageSectionInline(ReorderableInline):
    """Overview of a page's sections.

    Columns run in reading order — what the section is called, what type it is,
    whether it is live — and the button that opens it comes last, because it is
    the thing you do after reading the row rather than before.

    `show_change_link` stays off on purpose. Django's pencil and the button
    below lead to the same page, and two links to one place in a single row is
    what made this table hard to read.
    """

    model = PageSection
    extra = 0
    fields = ('heading', 'heading_en', 'kind', 'is_visible', 'order', 'edit_link')
    readonly_fields = ('edit_link',)
    ordering = ('order', 'id')
    show_change_link = False
    verbose_name = 'Sekcija'
    verbose_name_plural = 'Sekcije na ovoj stranici — prevucite da promijenite redoslijed'

    @admin.display(description='')
    def edit_link(self, obj):
        if not obj.pk:
            return mark_safe('<span class="inline-hint">Sačuvajte da biste dodali sadržaj</span>')
        count = obj.items.count()
        return format_html(
            '<a class="button button--open" href="{}">Uredi sadržaj</a>'
            '<span class="inline-count">{}</span>',
            reverse('admin:content_pagesection_change', args=[obj.pk]),
            f'{count} stavki' if count != 1 else '1 stavka',
        )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """The page's own title and intro paragraph.

    Off the home page: each site page now has its own entry there, and this
    form is reached from the "Naslov i uvod" link at the top of it. Changing a
    page's title is rare; changing what is on it is the daily job.
    """

    description = 'Naslov stranice i uvodni tekst ispod njega.'

    list_display = ('title', 'slug', 'section_count', 'changed')
    list_display_links = ('title',)
    search_fields = ('title', 'slug')
    actions = None
    inlines = [PageSectionInline]

    fieldsets = (
        ('Naslov stranice', {
            'fields': (('title', 'title_en'), ('intro', 'intro_en')),
            'description': 'Naslov i kratak tekst ispod njega. Uvod može ostati '
                           'prazan. ' + EN_NOTE,
        }),
        ('Tehnički podaci', {
            'fields': ('slug',),
            'classes': ('collapse',),
            'description': 'Adresa stranice na sajtu. Ne mijenjajte je bez potrebe.',
        }),
    )

    def get_model_perms(self, request):
        return {}

    @admin.display(description='Sekcija')
    def section_count(self, obj):
        return obj.sections.count()

    @admin.display(description='Izmijenjeno', ordering='updated_at')
    def changed(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y. %H:%M')


class PageContentAdmin(DragOrderedAdmin):
    """One site page, shown as the list of blocks that make it up.

    Subclasses set `page_slug` (through the proxy model) and nothing else. The
    queryset is pinned to that page, so the list is that page's contents and
    the page cannot be picked or changed by hand — a section belongs where it
    was created.
    """

    page_slug = None
    page_label = ''

    list_display = ('heading_display', 'kind', 'item_count', 'is_visible', 'site_link', 'delete_link')
    search_fields = ('heading', 'heading_en', 'body', 'items__title')
    list_display_links = ('heading_display',)
    list_filter = ()
    ordering = ('order', 'id')
    actions = None
    inlines = [SectionItemInline]

    fieldsets = (
        ('Naslov bloka', {
            'fields': (('heading', 'heading_en'), 'kind', 'is_visible'),
            'description': 'Naslov koji se vidi na sajtu i vrsta sadržaja koji ovaj '
                           'blok drži. ' + EN_NOTE,
        }),
        ('Tekst', {
            'fields': (('body', 'body_en'),),
            'description': 'Prazan red razdvaja pasuse. Za blokove sa dokumentima ili '
                           'linkovima ovo je uvodni tekst i može ostati prazno.',
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(page__slug=self.model.page_slug)

    def save_model(self, request, obj, form, change):
        """New blocks belong to this admin's page; nobody has to choose it."""
        if not change:
            obj.page = Page.objects.get(slug=self.model.page_slug)
            if not obj.order:
                last = self.get_queryset(request).order_by('-order').first()
                obj.order = (last.order + 1) if last else 0
        super().save_model(request, obj, form, change)

    @admin.display(description='Naslov bloka')
    def heading_display(self, obj):
        return obj.heading or f'({obj.get_kind_display()})'

    @admin.display(description='Sadržaja')
    def item_count(self, obj):
        count = obj.items.count()
        return f'{count} stavki' if count != 1 else '1 stavka'


def _register_page(proxy, label, text):
    """Register one site page as its own admin entry.

    The parameter is called `text` rather than `description` on purpose: inside
    a class body, `description = description` cannot see the enclosing
    function's local of the same name.
    """

    @admin.register(proxy)
    class _Admin(PageContentAdmin):
        page_label = label
        description = text
        site_path = '/' + proxy.page_slug

    return _Admin


_register_page(
    ProjektiPage,
    'Projekti',
    'Projekti Udruženja. Svaki projekat je jedna grupa — otvorite je da biste '
    'uređivali njegov opis i dokumente.',
)
_register_page(
    BibliotekaPage,
    'Biblioteka',
    'Stručna literatura i materijali, podijeljeni u grupe (stručni ispit, '
    'EU-OSHA kampanje).',
)
_register_page(
    RegulativaPage,
    'Regulativa',
    'Propisi na stranici Regulativa, podijeljeni u grupe. Svaka grupa je jedan '
    'podnaslov na sajtu — otvorite je da biste uređivali dokumente u njoj.',
)


class SinglePageAdmin(DragOrderedAdmin):
    """A page edited as one flat list, with no block layer in the way.

    The block still exists in the database, because the site renders pages out
    of blocks; it is just never shown. A new item is attached to the page's
    block, and the block is created on first use if the page has none yet.
    """

    page_slug = None
    page_label = ''
    item_noun = 'stavka'

    list_display = ('title', 'destination', 'site_link', 'delete_link')
    list_display_links = ('title',)
    search_fields = ('title', 'title_en', 'reference')
    ordering = ('order', 'id')
    actions = None

    fieldsets = (
        (None, {
            'fields': (('title', 'title_en'), ('description', 'description_en')),
            'description': 'Naziv koji se vidi na sajtu i, ako treba, kratak opis '
                           'ispod njega. ' + EN_NOTE,
        }),
        ('Gdje vodi', {
            'fields': ('url', 'file'),
            'description': 'Popunite samo jedno — adresu spoljne stranice, ili fajl '
                           'koji otpremate ovdje.',
        }),
        ('Dodatni podaci', {
            'fields': (('reference', 'reference_en'), 'date_label', 'pages', 'size_kb'),
            'classes': ('collapse',),
            'description': 'Sitni tekst ispod naziva — izvor, broj službenog lista, '
                           'datum. Veličina fajla se popunjava sama.',
        }),
        ('Fotografija', {
            'fields': ('image', 'image_url'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            section__page__slug=self.model.page_slug
        )

    def _section(self):
        """The page's single block, created on first use."""
        page = Page.objects.get(slug=self.model.page_slug)
        section = page.sections.order_by('order', 'id').first()
        if section is None:
            section = PageSection.objects.create(
                page=page,
                kind=PageSection.Kind.DOCUMENTS,
                order=0,
            )
        return section

    def save_model(self, request, obj, form, change):
        if not change:
            obj.section = self._section()
            if not obj.order:
                last = self.get_queryset(request).order_by('-order').first()
                obj.order = (last.order + 1) if last else 0
        super().save_model(request, obj, form, change)

    @admin.display(description='Vodi na')
    def destination(self, obj):
        target = obj.file.url if obj.file else obj.url
        if not target:
            return '—'
        return format_html('<a href="{}" target="_blank">{}</a>', target, target[:60])


def _register_single_page(proxy, label, text):
    """Register a page whose content is one flat list."""

    @admin.register(proxy)
    class _Admin(SinglePageAdmin):
        page_label = label
        description = text
        site_path = '/' + proxy.page_slug

    return _Admin


_register_single_page(
    PublikacijePage,
    'Publikacije',
    'Izdanja i dokumenti Udruženja, onim redom kojim se prikazuju na stranici Publikacije.',
)
_register_single_page(
    PressPage,
    'Press / Mediji',
    'Objave o Udruženju na drugim portalima. Naziv je naslov objave, „Gdje vodi“ '
    'je adresa članka, a „Izvor“ naziv medija.',
)
_register_single_page(
    PitanjaPage,
    'Pitanja i odgovori',
    'Pitanja sa stranice Pitanja i odgovori. Naziv je pitanje, opis je odgovor.',
)
