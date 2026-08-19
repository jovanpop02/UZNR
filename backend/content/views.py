import logging

from rest_framework import generics, status
from rest_framework.response import Response

from .emails import send_contact_emails
from .models import Announcement, ImportantLink, Member, NewsItem, Page
from .serializers import (
    AnnouncementSerializer,
    ContactMessageSerializer,
    ImportantLinkSerializer,
    MemberSerializer,
    NewsItemSerializer,
    PageSerializer,
)

logger = logging.getLogger(__name__)


class AnnouncementListView(generics.ListAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer


class NewsListView(generics.ListAPIView):
    queryset = NewsItem.objects.all()
    serializer_class = NewsItemSerializer


class NewsDetailView(generics.RetrieveAPIView):
    queryset = NewsItem.objects.all()
    serializer_class = NewsItemSerializer
    lookup_field = 'slug'


class MemberListView(generics.ListAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class ImportantLinkListView(generics.ListAPIView):
    queryset = ImportantLink.objects.all()
    serializer_class = ImportantLinkSerializer


class PageDetailView(generics.RetrieveAPIView):
    """Editable content for one page, both languages, sections in order."""

    queryset = Page.objects.prefetch_related('sections__items')
    serializer_class = PageSerializer
    lookup_field = 'slug'


class ContactCreateView(generics.CreateAPIView):
    """Accepts a contact-form submission and confirms it by e-mail."""

    serializer_class = ContactMessageSerializer
    throttle_scope = 'contact'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # A filled honeypot is a bot. Answer 201 anyway: telling a spammer that
        # its submission was dropped only teaches it to stop filling the field.
        if serializer.validated_data.get('website'):
            logger.info('Contact form honeypot triggered; submission discarded')
            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

        message = serializer.save()

        # The message is stored before any mail goes out, so a failing mail
        # server costs a confirmation, never the message itself.
        confirmation_ok, _ = send_contact_emails(message)

        return Response(
            {'status': 'ok', 'confirmation_sent': confirmation_ok},
            status=status.HTTP_201_CREATED,
        )
