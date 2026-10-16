"""Input normalisation shared by every form: phone numbers and "email or phone" contacts."""

from __future__ import annotations

import re
from typing import Literal

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

ContactKind = Literal["email", "phone"]

_SEPARATORS = re.compile(r"[\s.\-()/]")
# Cameroon: 9 digits, mobiles start with 6, landlines with 2. Optional 237 / +237 / 00237.
_CAMEROON = re.compile(r"^(?:\+?237|00237)?([26]\d{8})$")
# Any other country, in international format (E.164: up to 15 digits)
_INTERNATIONAL = re.compile(r"^(?:\+|00)([1-9]\d{7,14})$")


def normalize_phone(raw: str) -> str:
    """Return the number in E.164 (``+2376XXXXXXXX``) or raise ``ValidationError``."""
    compact = _SEPARATORS.sub("", raw or "")
    if match := _CAMEROON.match(compact):
        return f"+237{match.group(1)}"
    if match := _INTERNATIONAL.match(compact):
        return f"+{match.group(1)}"
    raise ValidationError(
        _("Numéro invalide. Exemple : 6 53 14 75 12 ou +237 6 53 14 75 12."), code="invalid_phone"
    )


def normalize_contact(raw: str) -> tuple[str, ContactKind]:
    """Accept an email address or a phone number and return it normalised with its kind."""
    value = (raw or "").strip()
    if "@" in value:
        try:
            validate_email(value)
        except ValidationError as exc:
            raise ValidationError(_("Adresse email invalide."), code="invalid_email") from exc
        return value.lower(), "email"
    try:
        return normalize_phone(value), "phone"
    except ValidationError as exc:
        raise ValidationError(
            _("Indiquez un email ou un numéro WhatsApp valide."), code="invalid_contact"
        ) from exc


def format_cameroon_display(e164: str) -> str:
    """``+237653147512`` -> ``653 147 512``; other countries are returned unchanged."""
    if e164.startswith("+237") and len(e164) == 13:
        local = e164[4:]
        return f"{local[:3]} {local[3:6]} {local[6:]}"
    return e164
