"""Email notifications to the shop. Always sent after the database transaction commits."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation

from .models import SiteSettings

logger = logging.getLogger(__name__)


def admin_change_url(app_label: str, model_name: str, pk: Any) -> str:
    path = reverse(f"admin:{app_label}_{model_name}_change", args=[pk])
    return f"{settings.ADMIN_URL_BASE.rstrip('/')}{path}"


def _send(subject: str, template: str, context: dict[str, Any]) -> None:
    try:
        recipient = SiteSettings.load().shop_notification_email
        # Shop staff read French regardless of the visitor's language
        with translation.override("fr"):
            body = render_to_string(template, context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except Exception:
        # The submission is already saved and visible in the admin: never fail the request.
        logger.exception("Shop notification failed: %s", subject)


def notify_shop_on_commit(subject: str, template: str, context: dict[str, Any]) -> None:
    transaction.on_commit(lambda: _send(subject, template, context))
