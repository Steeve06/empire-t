"""Shared abstract models and the site-wide content owned by the ``core`` app."""

from __future__ import annotations

import datetime as dt
from typing import Any, ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .images import ImageMeta, build_variants, delete_variants, validate_image_upload_size
from .validators import normalize_phone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    order = models.PositiveIntegerField(
        _("ordre d'affichage"),
        default=0,
        help_text=_("Les plus petits nombres s'affichent en premier."),
    )

    class Meta:
        abstract = True
        ordering = ("order", "id")


class OptimizedImagesModel(models.Model):
    """Re-encodes the image fields listed in ``optimized_image_fields`` as responsive WebP."""

    optimized_image_fields: ClassVar[tuple[str, ...]] = ()
    image_meta = models.JSONField(default=dict, blank=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        changed = self._process_images()
        update_fields = kwargs.get("update_fields")
        if changed and update_fields is not None:
            kwargs["update_fields"] = {*update_fields, "image_meta", *changed}
        super().save(*args, **kwargs)

    def _process_images(self) -> set[str]:
        changed: set[str] = set()
        for field_name in self.optimized_image_fields:
            file = getattr(self, field_name)
            previous: ImageMeta | None = self.image_meta.get(field_name)
            if file and not file._committed:
                upload_to = self._meta.get_field(field_name).upload_to  # type: ignore[union-attr]
                meta = build_variants(file, str(upload_to))
                delete_variants(file.storage, previous)
                setattr(self, field_name, meta["variants"][-1]["name"])
                self.image_meta[field_name] = meta
                changed.add(field_name)
            elif not file and previous:
                delete_variants(file.storage, previous)
                del self.image_meta[field_name]
                changed.add(field_name)
        return changed

    def delete_image_files(self) -> None:
        for field_name in self.optimized_image_fields:
            file = getattr(self, field_name)
            delete_variants(file.storage, self.image_meta.get(field_name))


class ContactKind(models.TextChoices):
    EMAIL = "email", _("Email")
    PHONE = "phone", _("WhatsApp / téléphone")


class PublicContent:
    """Marker: saving or deleting this model invalidates cached API responses."""

    invalidates_api_cache: ClassVar[bool] = True


class SiteSettings(PublicContent, OptimizedImagesModel):
    """Singleton holding everything the owner may want to change without a developer."""

    SINGLETON_PK = 1
    optimized_image_fields = ("hero_image", "signature_image", "about_image")

    business_name = models.CharField(_("nom du salon"), max_length=80, default="Empire T")
    business_subtitle = models.CharField(
        _("sous-titre"), max_length=80, default="Barbershop & Beauty"
    )
    tagline = models.CharField(_("slogan"), max_length=120)
    whatsapp_number = models.CharField(
        _("numéro WhatsApp"),
        max_length=20,
        help_text=_("Format international, par exemple +237653147512."),
    )
    email = models.EmailField(_("email public"))
    notification_email = models.EmailField(
        _("email de notification"),
        blank=True,
        help_text=_("Reçoit candidatures et messages. Vide = email public."),
    )
    address_line = models.CharField(_("adresse"), max_length=160)
    city = models.CharField(_("ville"), max_length=80, default="Yaoundé")
    country_code = models.CharField(_("code pays"), max_length=2, default="CM")
    opening_days_label = models.CharField(_("jours d'ouverture"), max_length=60)
    opening_time = models.TimeField(_("ouverture"), default=dt.time(7, 0))
    closing_time = models.TimeField(_("fermeture"), default=dt.time(21, 0))
    slot_interval_minutes = models.PositiveSmallIntegerField(
        _("intervalle des créneaux (min)"),
        default=30,
        validators=[MinValueValidator(10), MaxValueValidator(120)],
    )
    booking_horizon_days = models.PositiveSmallIntegerField(
        _("réservation possible jusqu'à (jours)"),
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
    )
    booking_lead_minutes = models.PositiveSmallIntegerField(
        _("délai minimum avant un créneau (min)"), default=30
    )
    accepts_mobile_money = models.BooleanField(_("Mobile Money accepté"), default=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    tiktok_url = models.URLField(_("TikTok"), blank=True)
    latitude = models.DecimalField(_("latitude"), max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_("longitude"), max_digits=9, decimal_places=6)
    maps_url = models.URLField(
        _("lien Google Maps"), blank=True, help_text=_("Lien « Itinéraire » partagé depuis Maps.")
    )
    recruitment_deadline = models.DateField(
        _("date limite des candidatures"), null=True, blank=True
    )
    application_documents = models.TextField(
        _("pièces du dossier de candidature"), help_text=_("Une pièce par ligne.")
    )
    story = models.TextField(_("notre histoire"))
    amenities = models.TextField(_("équipements et confort"), help_text=_("Un élément par ligne."))
    hero_image = models.ImageField(
        _("photo principale"),
        upload_to="site",
        blank=True,
        validators=[validate_image_upload_size],
    )
    signature_image = models.ImageField(
        _("photo du forfait signature"),
        upload_to="site",
        blank=True,
        validators=[validate_image_upload_size],
    )
    about_image = models.ImageField(
        _("photo du salon"), upload_to="site", blank=True, validators=[validate_image_upload_size]
    )
    signature_service = models.ForeignKey(
        "catalog.Service",
        verbose_name=_("prestation signature"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects: ClassVar[models.Manager[SiteSettings]] = models.Manager()

    class Meta:
        verbose_name = _("paramètres du site")
        verbose_name_plural = _("paramètres du site")
        constraints = [
            models.CheckConstraint(condition=models.Q(pk=1), name="site_settings_singleton"),
            models.CheckConstraint(
                condition=models.Q(closing_time__gt=models.F("opening_time")),
                name="site_settings_hours_order",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.business_name} {self.business_subtitle}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = self.SINGLETON_PK
        self.whatsapp_number = normalize_phone(self.whatsapp_number)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> SiteSettings:
        """Return the singleton. Raises DoesNotExist until ``manage.py seed`` has run."""
        return cls.objects.select_related("signature_service__category").get(pk=cls.SINGLETON_PK)

    @property
    def shop_notification_email(self) -> str:
        return self.notification_email or self.email

    @property
    def whatsapp_digits(self) -> str:
        return self.whatsapp_number.lstrip("+")

    @property
    def recruitment_open(self) -> bool:
        return (
            self.recruitment_deadline is not None
            and timezone.localdate() <= self.recruitment_deadline
        )

    @staticmethod
    def split_lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]


class Testimonial(PublicContent, OrderedModel, TimeStampedModel):
    author_name = models.CharField(_("nom du client"), max_length=80)
    author_location = models.CharField(_("quartier"), max_length=80, blank=True)
    quote = models.TextField(_("témoignage"), max_length=600)
    rating = models.PositiveSmallIntegerField(
        _("note"), default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_published = models.BooleanField(_("publié"), default=True)

    objects: ClassVar[models.Manager[Testimonial]] = models.Manager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("témoignage")
        verbose_name_plural = _("témoignages")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5), name="testimonial_rating_range"
            )
        ]
        indexes = [models.Index(fields=("is_published", "order"))]

    def __str__(self) -> str:
        return self.author_name


class TeamMember(PublicContent, OptimizedImagesModel, OrderedModel):
    optimized_image_fields = ("photo",)

    name = models.CharField(_("nom"), max_length=80)
    role = models.CharField(_("poste"), max_length=80)
    bio = models.TextField(_("présentation"), blank=True, max_length=600)
    photo = models.ImageField(
        _("photo"), upload_to="team", blank=True, validators=[validate_image_upload_size]
    )
    is_active = models.BooleanField(_("visible"), default=True)

    objects: ClassVar[models.Manager[TeamMember]] = models.Manager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("membre de l'équipe")
        verbose_name_plural = _("équipe")
        indexes = [models.Index(fields=("is_active", "order"))]

    def __str__(self) -> str:
        return self.name
