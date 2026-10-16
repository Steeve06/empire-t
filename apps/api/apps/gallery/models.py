from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.catalog.models import Service
from apps.core.images import validate_image_upload_size
from apps.core.models import OptimizedImagesModel, OrderedModel, PublicContent, TimeStampedModel


class GalleryCategory(models.TextChoices):
    CUTS = "cuts", _("Coupes")
    HAIRSTYLES = "hairstyles", _("Coiffures")
    BEAUTY = "beauty", _("Beauty")
    SALON = "salon", _("Le salon")


class GalleryImage(PublicContent, OptimizedImagesModel, OrderedModel, TimeStampedModel):
    optimized_image_fields = ("image",)

    category = models.CharField(_("catégorie"), max_length=12, choices=GalleryCategory.choices)
    image = models.ImageField(
        _("photo"), upload_to="gallery", validators=[validate_image_upload_size]
    )
    alt_text = models.CharField(
        _("description de la photo"),
        max_length=160,
        help_text=_("Décrit la photo pour les malvoyants et Google. Ex. : Skin fade avec motif."),
    )
    caption = models.CharField(_("légende"), max_length=120, blank=True)
    service = models.ForeignKey(
        Service,
        verbose_name=_("prestation liée"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_images",
        help_text=_("Active le bouton « Réserver ce style »."),
    )
    is_published = models.BooleanField(_("publiée"), default=True)
    is_featured = models.BooleanField(_("sur l'accueil"), default=False)

    objects: ClassVar[models.Manager[GalleryImage]] = models.Manager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("photo de la galerie")
        verbose_name_plural = _("galerie")
        indexes = [
            models.Index(fields=("is_published", "category", "order")),
            models.Index(
                fields=("order",),
                condition=Q(is_published=True, is_featured=True),
                name="gallery_featured_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.alt_text
