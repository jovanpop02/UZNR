"""Tests for the contact form and the page CMS.

Mail is asserted against Django's locmem outbox, so these run with no mail
server and no credentials. Delivery over real SMTP is a separate, manual check:
`manage.py send_test_email you@example.com` (see README).
"""

from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

from .models import ContactMessage, Page, PageSection, SectionItem

VALID_PAYLOAD = {
    'name': 'Marko Marković',
    'email': 'marko@primjer.me',
    'subject': 'Termin narednog stručnog ispita',
    'message': 'Zanima me termin narednog stručnog ispita i potrebna dokumentacija.',
    'language': 'mne',
}

def throttle_rate(rate):
    """Override the contact throttle for one test.

    `override_settings(REST_FRAMEWORK=...)` does not reach it: DRF binds
    `THROTTLE_RATES` onto the throttle class at import time, so the rate has to
    be patched on the class itself.
    """
    return patch.dict(ScopedRateThrottle.THROTTLE_RATES, {'contact': rate})


@override_settings(CONTACT_NOTIFY_EMAILS=['info@uznr.me'])
class ContactSubmissionTests(TestCase):
    url = '/api/contact'

    def setUp(self):
        # Throttle history lives in the cache and is keyed by client IP, which
        # every test shares. Without this, tests throttle each other.
        cache.clear()

    def post(self, **overrides):
        payload = {**VALID_PAYLOAD, **overrides}
        return self.client.post(self.url, payload, content_type='application/json')

    def test_valid_submission_is_stored(self):
        response = self.post()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 1)

        message = ContactMessage.objects.get()
        self.assertEqual(message.name, 'Marko Marković')
        self.assertEqual(message.email, 'marko@primjer.me')
        self.assertEqual(message.subject, 'Termin narednog stručnog ispita')
        self.assertEqual(message.status, ContactMessage.Status.NEW)

    def test_submission_sends_confirmation_and_notification(self):
        response = self.post()

        self.assertJSONEqual(response.content, {'status': 'ok', 'confirmation_sent': True})
        self.assertEqual(len(mail.outbox), 2)

        confirmation, notification = mail.outbox
        self.assertEqual(confirmation.to, ['marko@primjer.me'])
        self.assertEqual(notification.to, ['info@uznr.me'])

    def test_confirmation_quotes_the_message_back_in_both_parts(self):
        self.post()
        confirmation = mail.outbox[0]

        self.assertIn('Primili smo vašu poruku', confirmation.subject)
        self.assertIn('Marko Marković', confirmation.body)
        self.assertIn('stručnog ispita', confirmation.body)
        # The subject is free text now, quoted back exactly as it was typed.
        self.assertIn('Naslov: Termin narednog stručnog ispita', confirmation.body)

        html, content_type = confirmation.alternatives[0]
        self.assertEqual(content_type, 'text/html')
        self.assertIn('Primili smo vašu poruku', html)
        self.assertIn('Marko Marković', html)

        # Replying to the confirmation must reach the office, not the sender.
        self.assertEqual(confirmation.reply_to, ['info@uznr.me'])

    def test_confirmation_is_sent_in_english_when_the_form_was(self):
        self.post(language='en')
        confirmation = mail.outbox[0]

        self.assertIn('We have received your message', confirmation.subject)
        self.assertIn('Dear Marko Marković', confirmation.body)
        # The subject is the visitor's own words, so it is not translated.
        self.assertIn('Subject: Termin narednog stručnog ispita', confirmation.body)

    def test_notification_replies_to_the_sender(self):
        self.post()
        notification = mail.outbox[1]

        self.assertEqual(notification.reply_to, ['marko@primjer.me'])
        self.assertIn('Marko Marković', notification.body)
        self.assertIn('marko@primjer.me', notification.body)
        self.assertIn('Zanima me termin', notification.body)

    def test_successful_confirmation_is_timestamped(self):
        self.post()
        self.assertIsNotNone(ContactMessage.objects.get().confirmation_sent_at)

    def test_message_survives_a_broken_mail_server(self):
        # A dead SMTP host must cost the confirmation, never the message.
        with override_settings(
            MAILERS={'default': {'BACKEND': 'content.tests.FailingEmailBackend'}}
        ):
            response = self.post()

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {'status': 'ok', 'confirmation_sent': False})

        message = ContactMessage.objects.get()
        self.assertIsNone(message.confirmation_sent_at)

    def test_honeypot_submission_is_discarded_silently(self):
        response = self.post(website='http://spam.example')

        # 201 so a bot cannot tell the honeypot apart from a real submission.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_is_rejected(self):
        response = self.post(email='not-an-address')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_short_message_is_rejected_server_side(self):
        response = self.post(message='Zdravo')

        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.json())
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_blank_subject_is_rejected(self):
        response = self.post(subject='  ')

        self.assertEqual(response.status_code, 400)
        self.assertIn('subject', response.json())
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_unknown_language_falls_back_to_montenegrin(self):
        self.post(language='de')

        self.assertEqual(ContactMessage.objects.get().language, 'mne')
        self.assertIn('Primili smo vašu poruku', mail.outbox[0].subject)

    def test_subject_is_stored_and_echoed_verbatim(self):
        self.post(subject='  Pitanje o članstvu  ')

        message = ContactMessage.objects.get()
        self.assertEqual(message.subject, 'Pitanje o članstvu')
        # The visitor's own wording travels through to both e-mails.
        self.assertIn('Pitanje o članstvu', mail.outbox[0].body)


class FailingEmailBackend:
    """Stands in for an unreachable SMTP server."""

    def __init__(self, **kwargs):
        pass

    def send_messages(self, email_messages):
        raise OSError('SMTP server unreachable')


class ContactThrottleTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_repeated_submissions_are_throttled(self):
        with throttle_rate('2/hour'):
            for _ in range(2):
                response = self.client.post(
                    '/api/contact', VALID_PAYLOAD, content_type='application/json'
                )
                self.assertEqual(response.status_code, 201)

            blocked = self.client.post(
                '/api/contact', VALID_PAYLOAD, content_type='application/json'
            )

        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 2)


# Rendering an admin page resolves {% static %} through the manifest storage,
# which only exists after collectstatic. Tests should not depend on a build step.
@override_settings(
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
)
class ContactAdminTests(TestCase):
    """The inbox must not be editable or forgeable through the admin."""

    def setUp(self):
        from django.contrib.auth.models import User

        self.admin_user = User.objects.create_superuser('staff', 'staff@uznr.me', 'pw-for-tests')
        self.client.force_login(self.admin_user)
        self.message = ContactMessage.objects.create(**{
            key: value for key, value in VALID_PAYLOAD.items() if key != 'website'
        })

    def test_messages_cannot_be_created_in_the_admin(self):
        response = self.client.get('/admin/content/contactmessage/add/')
        self.assertEqual(response.status_code, 403)

    def test_change_form_shows_the_message_read_only(self):
        response = self.client.get(f'/admin/content/contactmessage/{self.message.pk}/change/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marko Marković')
        # Editable fields are rendered as inputs; the message body must not be.
        self.assertNotContains(response, 'name="message"')
        self.assertContains(response, 'name="status"')

    def test_resend_confirmation_action_sends_again(self):
        self.client.post(
            '/admin/content/contactmessage/',
            {'action': 'resend_confirmation', '_selected_action': [str(self.message.pk)]},
            follow=True,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['marko@primjer.me'])
        self.message.refresh_from_db()
        self.assertIsNotNone(self.message.confirmation_sent_at)


class PageApiTests(TestCase):
    def setUp(self):
        self.page = Page.objects.create(
            slug='regulativa',
            title='Regulativa',
            title_en='Regulations',
            intro='Zakoni i pravilnici.',
        )
        self.section = PageSection.objects.create(
            page=self.page,
            kind=PageSection.Kind.DOCUMENTS,
            heading='Zakoni',
            heading_en='Laws',
            order=0,
        )
        SectionItem.objects.create(
            section=self.section, title='Zakon o zaštiti na radu', url='https://example.me/zakon', order=0
        )

    def test_page_is_served_with_sections_and_items(self):
        response = self.client.get(reverse('page-detail', args=['regulativa']))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['slug'], 'regulativa')
        self.assertEqual(data['title'], {'mne': 'Regulativa', 'en': 'Regulations'})
        self.assertEqual(len(data['sections']), 1)

        section = data['sections'][0]
        self.assertEqual(section['kind'], 'documents')
        self.assertEqual(section['heading'], {'mne': 'Zakoni', 'en': 'Laws'})
        self.assertEqual(section['items'][0]['href'], 'https://example.me/zakon')

    def test_english_falls_back_to_montenegrin_when_blank(self):
        response = self.client.get(reverse('page-detail', args=['regulativa']))
        item = response.json()['sections'][0]['items'][0]

        self.assertEqual(item['title'], {'mne': 'Zakon o zaštiti na radu', 'en': 'Zakon o zaštiti na radu'})

    def test_hidden_sections_are_not_served(self):
        self.section.is_visible = False
        self.section.save()

        response = self.client.get(reverse('page-detail', args=['regulativa']))

        self.assertEqual(response.json()['sections'], [])

    def test_sections_come_back_in_admin_order(self):
        PageSection.objects.create(page=self.page, heading='Posljednja', order=99)

        headings = [
            section['heading']['mne']
            for section in self.client.get(reverse('page-detail', args=['regulativa'])).json()['sections']
        ]

        self.assertEqual(headings[-1], 'Posljednja')

    def test_unknown_page_is_404(self):
        self.assertEqual(self.client.get('/api/pages/ne-postoji').status_code, 404)

    def test_site_relative_document_paths_are_valid_links(self):
        # Most documents on this site are published by the frontend, so an item
        # pointing at /documents/... must pass validation — a URLField here made
        # every seeded item unsaveable in the admin.
        item = SectionItem(
            section=self.section,
            title='Zakon',
            url='/documents/regulativa/zakon.pdf',
        )
        item.full_clean()  # must not raise

    def test_nonsense_links_are_still_rejected(self):
        item = SectionItem(section=self.section, title='Loš link', url='ovo nije adresa')

        with self.assertRaises(DjangoValidationError):
            item.full_clean()

    def test_size_is_filled_in_from_an_uploaded_file(self):
        item = SectionItem(section=self.section, title='Dokument')
        item.file.save('probni.pdf', ContentFile(b'x' * 4096), save=False)
        item.save()

        self.assertEqual(item.size_kb, 4)
        item.file.delete(save=False)
