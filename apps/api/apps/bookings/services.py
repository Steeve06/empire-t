"""Booking business rules: which time slots are offered, and the WhatsApp hand-off message."""

from __future__ import annotations

import datetime as dt

from django.utils import timezone

from apps.catalog.models import Service
from apps.core.models import SiteSettings
from apps.core.validators import format_cameroon_display
from apps.core.whatsapp import whatsapp_link

from .models import BookingRequest

FR_DAYS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
FR_MONTHS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def bookable_dates(site: SiteSettings, today: dt.date) -> tuple[dt.date, dt.date]:
    return today, today + dt.timedelta(days=site.booking_horizon_days)


def available_slots(
    site: SiteSettings,
    day: dt.date,
    service: Service | None = None,
    now: dt.datetime | None = None,
) -> list[dt.time]:
    """Start times offered on ``day``.

    A slot is offered when the service (shortest duration) ends before closing time and, for
    today, when it starts at least ``booking_lead_minutes`` from now. Capacity is not checked
    in v1: the shop confirms each request on WhatsApp (see docs/decisions.md, ADR-008).
    """
    now = timezone.localtime(now or timezone.now())
    first_day, last_day = bookable_dates(site, now.date())
    if not first_day <= day <= last_day:
        return []

    duration = dt.timedelta(minutes=service.duration_min if service else site.slot_interval_minutes)
    step = dt.timedelta(minutes=site.slot_interval_minutes)
    opening = dt.datetime.combine(day, site.opening_time)
    closing = dt.datetime.combine(day, site.closing_time)
    earliest = (now + dt.timedelta(minutes=site.booking_lead_minutes)).replace(tzinfo=None)

    slots: list[dt.time] = []
    current = opening
    while current + duration <= closing:
        if current >= earliest:
            slots.append(current.time())
        current += step
    return slots


def _format_date(day: dt.date, language: str) -> str:
    if language == "en":
        return f"{day:%A} {day.day} {day:%B} {day.year}"
    return f"{FR_DAYS[day.weekday()]} {day.day} {FR_MONTHS[day.month - 1]} {day.year}"


def _format_time(value: dt.time, language: str) -> str:
    return value.strftime("%H:%M") if language == "en" else value.strftime("%Hh%M")


def booking_message(booking: BookingRequest) -> str:
    language = booking.locale
    date_label = _format_date(booking.date, language)
    time_label = _format_time(booking.time_slot, language)
    phone = format_cameroon_display(booking.phone)
    if language == "en":
        lines = [
            "Hello Empire T! I would like to book:",
            f"• Service: {booking.service_name}",
            f"• Date: {date_label}",
            f"• Time: {time_label}",
            f"• Name: {booking.customer_name}",
            f"• Phone: {phone}",
        ]
        if booking.notes:
            lines.append(f"• Note: {booking.notes}")
        lines.append(f"Reference: {booking.reference}")
    else:
        lines = [
            "Bonjour Empire T ! Je souhaite réserver :",
            f"• Prestation : {booking.service_name}",
            f"• Date : {date_label}",
            f"• Heure : {time_label}",
            f"• Nom : {booking.customer_name}",
            f"• Téléphone : {phone}",
        ]
        if booking.notes:
            lines.append(f"• Note : {booking.notes}")
        lines.append(f"Référence : {booking.reference}")
    return "\n".join(lines)


def shop_whatsapp_url(booking: BookingRequest, site: SiteSettings) -> str:
    """Link the customer opens to send the prefilled request to the shop."""
    return whatsapp_link(site.whatsapp_number, booking_message(booking))


def customer_whatsapp_url(booking: BookingRequest) -> str:
    """Link the owner opens from the admin to confirm with the customer."""
    if booking.locale == "en":
        text = (
            f"Hello {booking.customer_name}, Empire T here. Your booking {booking.reference} "
            f"({booking.service_name}) on {_format_date(booking.date, 'en')} at "
            f"{_format_time(booking.time_slot, 'en')} is confirmed. See you soon!"
        )
    else:
        text = (
            f"Bonjour {booking.customer_name}, ici Empire T. Votre réservation "
            f"{booking.reference} ({booking.service_name}) du "
            f"{_format_date(booking.date, 'fr')} à {_format_time(booking.time_slot, 'fr')} "
            "est confirmée. À très bientôt !"
        )
    return whatsapp_link(booking.phone, text)
