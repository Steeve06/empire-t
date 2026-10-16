from __future__ import annotations

import datetime as dt
import secrets
from pathlib import PurePath
from typing import ClassVar

from django.core.files.storage import Storage, storages
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import (
    ContactKind,
    OrderedModel,
    PublicContent,
    SiteSettings,
    TimeStampedModel,
)


def private_storage() -> Storage:
    """Application documents are never publicly reachable (see settings STORAGES["private"])."""
    return storages["private"]


def application_upload_path(instance: ApplicationFile, filename: str) -> str:
    today = timezone.localdate()
    suffix = PurePath(filename).suffix.lower()
    return f"applications/{today:%Y/%m}/{secrets.token_hex(12)}{suffix}"


class JobOpeningQuerySet(models.QuerySet["JobOpening"]):
    def open_on(self, day: dt.date, site: SiteSettings) -> JobOpeningQuerySet:
        """Active openings whose own deadline (or the global one) has not passed."""
        if not site.recruitment_deadline or day > site.recruitment_deadline:
            return self.none()
        return self.filter(is_active=True).filter(
            models.Q(deadline__isnull=True) | models.Q(deadline__gte=day)
        )


class JobOpeningManager(models.Manager["JobOpening"]):
    def get_queryset(self) -> JobOpeningQuerySet:
        return JobOpeningQuerySet(self.model, using=self._db)

    def open_on(self, day: dt.date, site: SiteSettings) -> JobOpeningQuerySet:
        return self.get_queryset().open_on(day, site)


class JobOpening(PublicContent, OrderedModel, TimeStampedModel):
    slug = models.SlugField(_("identifiant"), unique=True)
    title = models.CharField(_("intitulé du poste"), max_length=100)
    positions_count = models.PositiveSmallIntegerField(
        _("nombre de postes"), default=1, validators=[MinValueValidator(1)]
    )
    requirements = models.CharField(_("profil recherché"), max_length=240)
    description = models.TextField(_("description"), blank=True, max_length=1200)
    deadline = models.DateField(
        _("date limite propre"),
        null=True,
        blank=True,
        help_text=_("Vide = date limite générale des paramètres du site."),
    )
    is_active = models.BooleanField(_("publiée"), default=True)

    objects: ClassVar[JobOpeningManager] = JobOpeningManager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("offre d'emploi")
        verbose_name_plural = _("offres d'emploi")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(positions_count__gte=1), name="opening_positions_positive"
            )
        ]

    def __str__(self) -> str:
        return self.title

    def effective_deadline(self, site: SiteSettings) -> dt.date | None:
        deadlines = [d for d in (self.deadline, site.recruitment_deadline) if d is not None]
        return min(deadlines) if deadlines else None


class ApplicationStatus(models.TextChoices):
    NEW = "new", _("Nouvelle")
    REVIEWING = "reviewing", _("En cours d'examen")
    INTERVIEW = "interview", _("Entretien prévu")
    REJECTED = "rejected", _("Non retenue")
    HIRED = "hired", _("Recruté(e)")


class JobApplication(TimeStampedModel):
    opening = models.ForeignKey(
        JobOpening, verbose_name=_("poste"), on_delete=models.PROTECT, related_name="applications"
    )
    full_name = models.CharField(_("nom complet"), max_length=100)
    contact = models.CharField(_("email ou WhatsApp"), max_length=254)
    contact_kind = models.CharField(_("type de contact"), max_length=8, choices=ContactKind.choices)
    message = models.TextField(_("message"), blank=True, max_length=1000)
    status = models.CharField(
        _("statut"),
        max_length=12,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
    )
    locale = models.CharField(_("langue"), max_length=2, default="fr")
    internal_notes = models.TextField(_("notes internes"), blank=True)

    class Meta:
        verbose_name = _("candidature")
        verbose_name_plural = _("candidatures")
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("status", "created_at"))]

    def __str__(self) -> str:
        return f"{self.full_name} · {self.opening}"


class ApplicationFile(models.Model):
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("candidature"),
    )
    file = models.FileField(
        _("fichier"), storage=private_storage, upload_to=application_upload_path, max_length=200
    )
    original_name = models.CharField(_("nom d'origine"), max_length=120)
    kind = models.CharField(_("type"), max_length=8)
    content_type = models.CharField(_("type MIME"), max_length=100)
    size = models.PositiveIntegerField(_("taille (octets)"))
    uploaded_at = models.DateTimeField(_("reçu le"), auto_now_add=True)

    class Meta:
        verbose_name = _("pièce jointe")
        verbose_name_plural = _("pièces jointes")
        ordering = ("id",)

    def __str__(self) -> str:
        return self.original_name
