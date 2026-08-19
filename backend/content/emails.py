"""Outgoing mail for the contact form.

Two messages go out per submission:

  * a confirmation to the person who wrote in, so they know the message landed
    and what the Association received;
  * a notification to the office, with a Reply-To pointing at the sender so
    staff can answer straight from their inbox.

Nothing in here is allowed to break a submission. The message is already saved
by the time these run, so a mail server that is down must cost us a log line
and a blank `confirmation_sent_at`, never a 500 for the visitor — the admin
list shows which confirmations failed and can resend them.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# The confirmation is sent in whichever language the visitor was reading.
SUBJECTS = {
    'mne': 'Primili smo vašu poruku — UZNR Crne Gore',
    'en': 'We have received your message — OSH Association of Montenegro',
}


def _context(message):
    return {
        'message': message,
        'site_url': settings.SITE_URL,
        'office_email': settings.CONTACT_OFFICE_EMAIL,
        'office_phone': settings.CONTACT_OFFICE_PHONE,
        'admin_url': (
            f'{settings.BACKEND_URL}/admin/content/contactmessage/{message.pk}/change/'
        ),
    }


def send_confirmation(message):
    """Confirm receipt to the sender. Returns True when the mail was accepted."""
    lang = 'en' if message.language == 'en' else 'mne'
    context = _context(message)

    mail = EmailMultiAlternatives(
        subject=SUBJECTS[lang],
        body=render_to_string(f'email/contact_confirmation.{lang}.txt', context),
        to=[message.email],
        reply_to=[settings.CONTACT_OFFICE_EMAIL],
    )
    mail.attach_alternative(
        render_to_string(f'email/contact_confirmation.{lang}.html', context), 'text/html'
    )

    try:
        mail.send()
    except Exception:
        logger.exception('Contact confirmation to %s failed', message.email)
        return False

    message.mark_confirmation_sent()
    return True


def send_office_notification(message):
    """Forward the message to the Association's inbox. Returns True on success."""
    recipients = settings.CONTACT_NOTIFY_EMAILS
    if not recipients:
        logger.warning('No CONTACT_NOTIFY_EMAILS configured; message %s not forwarded', message.pk)
        return False

    mail = EmailMultiAlternatives(
        subject=f'[Sajt] {message.subject} — {message.name}',
        body=render_to_string('email/contact_notification.txt', _context(message)),
        to=recipients,
        # So "Reply" in the office inbox goes to the visitor, not to ourselves.
        reply_to=[message.email],
    )

    try:
        mail.send()
    except Exception:
        logger.exception('Contact notification for message %s failed', message.pk)
        return False

    return True


def send_contact_emails(message):
    """Send both messages. Returns (confirmation_ok, notification_ok)."""
    return send_confirmation(message), send_office_notification(message)
