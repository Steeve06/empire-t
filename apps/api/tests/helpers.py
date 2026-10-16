from __future__ import annotations

import datetime as dt
from urllib.parse import parse_qs, urlparse

from django.utils import timezone


def future_date(days: int = 3) -> dt.date:
    return timezone.localdate() + dt.timedelta(days=days)


def whatsapp_text(url: str) -> str:
    """Decoded prefilled message of a wa.me link."""
    return parse_qs(urlparse(url).query)["text"][0]
