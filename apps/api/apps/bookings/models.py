"""Booking requests.

Version 1 is request-based: the customer sends a request, the shop confirms on WhatsApp.
The model already stores everything slot availability and payments will need, so those can be
added later with new code and nullable/defaulted columns only:

* ``duration_minutes`` snapshot + ``starts_at``/``ends_at`` -> overlap checks per chair/staff
* ``status`` lifecycle -> only CONFIRMED rows will block a slot
* ``payment_status`` / ``amount_due`` / ``payment_reference`` -> Mobile Money deposits
* price and name snapshots -> history stays correct when the owner edits the menu
"""

from __future__ import annotations

import datetime as dt
import secrets

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.catalog.models import Service
from apps.core.models import TimeStampedModel

REFERENCE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L
REFERENCE_LENGTH = 6


def generate_reference() -> str:
    return "ET-" + "".join(secrets.choice(REFERENCE_ALPHABET) for _ in range(REFERENCE_LENGTH))


class BookingStatus(models.TextChoices):
    NEW = "new", _("Nouvelle")
    CONFIRMED = "confirmed", _("Confirmée")
    COMPLETED = "completed", _("Honorée")
    CANCELLED = "cancelled", _("Annulée")
    NO_SHOW = "no_show", _("Absent")


class PaymentStatus(models.TextChoices):
    NOT_REQUIRED = "not_required", _("Non requis")
    PENDING = "pending", _("En attente")
    PAID = "paid", _("Payé")
    REFUNDED = "refunded", _("Remboursé")


class BookingChannel(models.TextChoices):
    WEBSITE = "website", _("Page Réserver")
    QUICK_BAR = "quick_bar", _("Barre de réservation (accueil)")
    ADMIN = "admin", _("Saisie manuelle")


class BookingRequest(TimeStampedModel):
    reference = models.CharField(
        _("référence"), max_length=12, unique=True, default=generate_reference, editable=False
    )
    service = models.ForeignKey(
        Service, verbose_name=_("prestation"), on_delete=models.PROTECT, related_name="bookings"
    )
    service_name = models.CharField(_("prestation (au moment de la demande)"), max_length=120)
    price_snapshot = models.PositiveIntegerField(_("prix affiché (FCFA)"), null=True, blank=True)
    price_is_from = models.BooleanField(_("prix « dès »"), default=False)
    duration_minutes = models.PositiveSmallIntegerField(_("durée prévue (min)"))
    date = models.DateField(_("date"))
    time_slot = models.TimeField(_("heure"))
    customer_name = models.CharField(_("nom du client"), max_length=80)
    phone = models.CharField(_("téléphone"), max_length=20)
    notes = models.TextField(_("message du client"), blank=True, max_length=500)
    status = models.CharField(
        _("statut"), max_length=12, choices=BookingStatus.choices, default=BookingStatus.NEW
    )
    channel = models.CharField(
        _("origine"), max_length=12, choices=BookingChannel.choices, default=BookingChannel.WEBSITE
    )
    locale = models.CharField(_("langue"), max_length=2, default="fr")
    payment_status = models.CharField(
        _("paiement"),
        max_length=12,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_REQUIRED,
    )
    amount_due = models.PositiveIntegerField(_("montant dû (FCFA)"), default=0)
    payment_reference = models.CharField(_("référence de paiement"), max_length=64, blank=True)
    internal_notes = models.TextField(_("notes internes"), blank=True)

    class Meta:
        verbose_name = _("demande de réservation")
        verbose_name_plural = _("demandes de réservation")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("date", "time_slot")),
            models.Index(fields=("status", "date")),
            models.Index(fields=("phone",)),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_minutes__gt=0), name="booking_duration_positive"
            )
        ]

    def __str__(self) -> str:
        return f"{self.reference} · {self.customer_name}"

    @property
    def starts_at(self) -> dt.datetime:
        return timezone.make_aware(dt.datetime.combine(self.date, self.time_slot))

    @property
    def ends_at(self) -> dt.datetime:
        return self.starts_at + dt.timedelta(minutes=self.duration_minutes)
