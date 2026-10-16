from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import ContactKind, TimeStampedModel


class MessageStatus(models.TextChoices):
    NEW = "new", _("Nouveau")
    READ = "read", _("Lu")
    ANSWERED = "answered", _("Répondu")
    ARCHIVED = "archived", _("Archivé")


class ContactMessage(TimeStampedModel):
    name = models.CharField(_("nom"), max_length=80)
    contact = models.CharField(_("email ou téléphone"), max_length=254)
    contact_kind = models.CharField(_("type de contact"), max_length=8, choices=ContactKind.choices)
    message = models.TextField(_("message"), max_length=2000)
    status = models.CharField(
        _("statut"), max_length=10, choices=MessageStatus.choices, default=MessageStatus.NEW
    )
    locale = models.CharField(_("langue"), max_length=2, default="fr")

    class Meta:
        verbose_name = _("message de contact")
        verbose_name_plural = _("messages de contact")
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("status", "created_at"))]

    def __str__(self) -> str:
        return f"{self.name} ({self.created_at:%d/%m/%Y})"
