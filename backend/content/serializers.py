from rest_framework import serializers

from .models import (
    Announcement,
    AnnouncementLink,
    ContactMessage,
    ImportantLink,
    Member,
    NewsImage,
    NewsItem,
    Page,
    PageSection,
    SectionItem,
)


def absolute(request, url):
    """Media URLs must be absolute — the frontend is on a different origin."""
    return request.build_absolute_uri(url) if request else url


def localized(mne, en):
    """Emit both languages for one field.

    The frontend switches language client-side without refetching, so every
    text field ships in both languages and the page picks one. English falls
    back to Montenegrin, which is what an unfilled EN field should mean.
    """
    return {'mne': mne, 'en': en or mne}


class NewsImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsImage
        fields = ['image', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class NewsItemSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    images = NewsImageSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = NewsItem
        fields = ['slug', 'title', 'excerpt', 'date', 'thumbnail', 'content', 'images']

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    def get_excerpt(self, obj):
        return localized(obj.excerpt, obj.excerpt_en)

    def get_content(self, obj):
        return localized(obj.content or '', obj.content_en)

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        request = self.context.get('request')
        url = obj.thumbnail.url
        return request.build_absolute_uri(url) if request else url


class AnnouncementLinkSerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = AnnouncementLink
        fields = ['title', 'href']

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    def get_href(self, obj):
        if obj.file:
            request = self.context.get('request')
            url = obj.file.url
            return request.build_absolute_uri(url) if request else url
        return obj.url


class AnnouncementSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    links = AnnouncementLinkSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    link_label = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'excerpt', 'date', 'photo', 'link', 'link_label', 'is_open', 'links']

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    def get_excerpt(self, obj):
        return localized(obj.excerpt, obj.excerpt_en)

    def get_link_label(self, obj):
        return localized(obj.link_label, obj.link_label_en)

    def get_photo(self, obj):
        if not obj.photo:
            return None
        request = self.context.get('request')
        url = obj.photo.url
        return request.build_absolute_uri(url) if request else url


class ImportantLinkSerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()
    is_file = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    class Meta:
        model = ImportantLink
        fields = ['title', 'href', 'is_file', 'logo']

    def get_href(self, obj):
        if obj.file:
            request = self.context.get('request')
            url = obj.file.url
            return request.build_absolute_uri(url) if request else url
        return obj.url

    def get_is_file(self, obj):
        return bool(obj.file)

    def get_logo(self, obj):
        if not obj.logo:
            return None
        request = self.context.get('request')
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url


class MemberSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['name', 'url', 'logo']

    def get_logo(self, obj):
        if not obj.logo:
            return None
        request = self.context.get('request')
        url = obj.logo.url
        return request.build_absolute_uri(url) if request else url


class ContactMessageSerializer(serializers.ModelSerializer):
    """Validates and stores one contact-form submission.

    `website` is a honeypot: the form renders it hidden, so a human never fills
    it in and anything that does is a bot. It is write-only and never stored.
    """

    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message', 'language', 'website']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Unesite ime i prezime.')
        return value

    def validate_subject(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('Unesite naslov poruke.')
        return value

    def validate_message(self, value):
        value = value.strip()
        # Mirrors the browser-side rule, because client validation is only a
        # convenience — anything can POST here.
        if len(value) < 20:
            raise serializers.ValidationError('Poruka treba da ima najmanje 20 karaktera.')
        return value

    def validate_language(self, value):
        return 'en' if value == 'en' else 'mne'

    def create(self, validated_data):
        validated_data.pop('website', None)
        return super().create(validated_data)


class SectionItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    is_file = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    reference = serializers.SerializerMethodField()

    class Meta:
        model = SectionItem
        fields = [
            'id', 'title', 'description', 'href', 'is_file', 'image',
            'reference', 'date_label', 'pages', 'size_kb', 'order',
        ]

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    def get_reference(self, obj):
        return localized(obj.reference, obj.reference_en)

    def get_description(self, obj):
        return localized(obj.description, obj.description_en)

    def get_href(self, obj):
        if obj.file:
            return absolute(self.context.get('request'), obj.file.url)
        return obj.url or None

    def get_is_file(self, obj):
        return bool(obj.file)

    def get_image(self, obj):
        if obj.image:
            return absolute(self.context.get('request'), obj.image.url)
        # A path like /press/slika.jpg is served by the frontend, so it is
        # returned as-is for the browser to resolve against the site itself.
        return obj.image_url or None


class PageSectionSerializer(serializers.ModelSerializer):
    heading = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    items = SectionItemSerializer(many=True, read_only=True)

    class Meta:
        model = PageSection
        fields = ['id', 'kind', 'heading', 'body', 'items', 'order']

    def get_heading(self, obj):
        return localized(obj.heading, obj.heading_en)

    def get_body(self, obj):
        return localized(obj.body, obj.body_en)


class PageSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['slug', 'title', 'intro', 'sections', 'updated_at']

    def get_title(self, obj):
        return localized(obj.title, obj.title_en)

    def get_intro(self, obj):
        return localized(obj.intro, obj.intro_en)

    def get_sections(self, obj):
        visible = [section for section in obj.sections.all() if section.is_visible]
        return PageSectionSerializer(visible, many=True, context=self.context).data
