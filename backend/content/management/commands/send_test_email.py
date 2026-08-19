"""Verify the mail configuration against the real mail server.

The test suite proves the messages are built correctly, but it never opens a
socket. This command is the other half: it sends a genuine contact confirmation
through whatever MAILERS backend the environment configures, so a wrong SMTP
host, a rejected password or a From address the provider refuses to relay shows
up as an error here instead of as silence in production.

    python manage.py send_test_email you@example.com
    python manage.py send_test_email you@example.com --lang en
    python manage.py send_test_email you@example.com --keep

Nothing is stored: the message is created in memory and rolled back, unless
--keep is passed.
"""

from django.conf import settings
from django.core.mail import mailers
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from content.emails import send_confirmation, send_office_notification
from content.models import ContactMessage


class Command(BaseCommand):
    help = 'Sends a test contact confirmation to the given address.'

    def add_arguments(self, parser):
        parser.add_argument('recipient', help='Address to send the test confirmation to.')
        parser.add_argument('--lang', choices=['mne', 'en'], default='mne', help='Language of the confirmation.')
        parser.add_argument('--keep', action='store_true', help='Keep the test message in the database.')
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Also send the office notification to CONTACT_NOTIFY_EMAILS.',
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        backend = mailers.settings.get('default', {}).get('BACKEND', '')

        self.stdout.write(f'Mailer:    {backend}')
        self.stdout.write(f'From:      {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'To:        {recipient}')
        if 'console' in backend:
            self.stdout.write(
                self.style.WARNING(
                    'EMAIL_HOST is not set, so this only prints below — nothing is delivered.'
                )
            )

        with transaction.atomic():
            message = ContactMessage.objects.create(
                name='Test poruka',
                email=recipient,
                subject='Probna poruka',
                message=(
                    'Ovo je probna poruka poslata komandom send_test_email radi provjere '
                    f'podešavanja mejla. Vrijeme: {timezone.localtime():%d.%m.%Y. %H:%M}.'
                ),
                language=options['lang'],
            )

            sent = send_confirmation(message)
            notified = send_office_notification(message) if options['notify'] else None

            if not options['keep']:
                transaction.set_rollback(True)

        if not sent:
            raise CommandError(
                'Sending failed. The traceback above has the reason — check EMAIL_HOST, '
                'EMAIL_HOST_USER, EMAIL_HOST_PASSWORD and DEFAULT_FROM_EMAIL.'
            )

        self.stdout.write(self.style.SUCCESS(f'Confirmation accepted by the mail server for {recipient}.'))
        if notified is False:
            self.stdout.write(self.style.ERROR('Office notification failed — see the traceback above.'))
        elif notified:
            self.stdout.write(
                self.style.SUCCESS(f'Office notification sent to {", ".join(settings.CONTACT_NOTIFY_EMAILS)}.')
            )
        self.stdout.write('Check the inbox (and the spam folder) to confirm it actually arrived.')
