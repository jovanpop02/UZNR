"""Template context shared across the admin."""

from .models import ContactMessage


def admin_inbox(request):
    """Unanswered-message count for the inbox button in the admin header.

    The button sits in the header on every admin page, so the count has to be
    available to every admin template rather than just the dashboard.

    Only staff sessions pay for the query: anonymous requests and the public API
    return an empty context and never touch the table.
    """
    user = getattr(request, 'user', None)
    if user is None or not user.is_active or not user.is_staff:
        return {}

    return {
        'uznr_inbox_waiting': ContactMessage.objects.filter(
            status=ContactMessage.Status.NEW
        ).count(),
    }
