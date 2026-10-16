from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Min, Prefetch, Q
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from apps.core.images import validate_image_upload_size
from apps.core.models import OptimizedImagesModel, OrderedModel, PublicContent, TimeStampedModel


class Accent(models.TextChoices):
    GOLD = "gold", _("Or")
    ROSE = "rose", _("Rose (Beauty & Spa)")


class ServiceCategoryQuerySet(models.QuerySet["ServiceCategory"]):
    def with_active_services(self) -> ServiceCategoryQuerySet:
        """Active categories, their active services prefetched and the lowest price annotated."""
        return (
            self.filter(is_active=True)
            .annotate(starting_price=Min("services__price", filter=Q(services__is_active=True)))
            .prefetch_related(
                Prefetch(
                    "services",
                    queryset=Service.objects.filter(is_active=True).order_by("order", "id"),
                    to_attr="active_services",
                )
            )
        )


if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager


class ServiceCategoryManager(models.Manager["ServiceCategory"]):
    def get_queryset(self) -> ServiceCategoryQuerySet:
        return ServiceCategoryQuerySet(self.model, using=self._db)

    def with_active_services(self) -> ServiceCategoryQuerySet:
        return self.get_queryset().with_active_services()


class ServiceCategory(PublicContent, OptimizedImagesModel, OrderedModel, TimeStampedModel):
    optimized_image_fields = ("image",)

    slug = models.SlugField(
        _("identifiant d'URL"), unique=True, help_text=_("Utilisé dans l'adresse de l'onglet.")
    )
    name = models.CharField(_("nom court (onglet)"), max_length=60)
    title = models.CharField(_("titre (menu et cartes)"), max_length=80)
    tagline = models.CharField(_("accroche"), max_length=140, blank=True)
    booking_note = models.CharField(
        _("note de réservation"), max_length=120, blank=True, help_text=_("Ex. : Sur rendez-vous.")
    )
    accent = models.CharField(_("couleur d'accent"), max_length=8, choices=Accent.choices)
    appointment_only = models.BooleanField(_("sur rendez-vous uniquement"), default=False)
    show_on_home = models.BooleanField(_("afficher sur l'accueil"), default=True)
    image = models.ImageField(
        _("photo"), upload_to="categories", blank=True, validators=[validate_image_upload_size]
    )
    is_active = models.BooleanField(_("visible"), default=True)

    objects: ClassVar[ServiceCategoryManager] = ServiceCategoryManager()
    if TYPE_CHECKING:
        services: RelatedManager[Service]

    class Meta(OrderedModel.Meta):
        verbose_name = _("catégorie")
        verbose_name_plural = _("catégories")
        indexes = [models.Index(fields=("is_active", "order"))]

    def __str__(self) -> str:
        return self.title


class ServiceQuerySet(models.QuerySet["Service"]):
    def active(self) -> ServiceQuerySet:
        return self.filter(is_active=True, category__is_active=True)


class ServiceManager(models.Manager["Service"]):
    def get_queryset(self) -> ServiceQuerySet:
        return ServiceQuerySet(self.model, using=self._db)

    def active(self) -> ServiceQuerySet:
        return self.get_queryset().active()


class Service(PublicContent, OptimizedImagesModel, OrderedModel, TimeStampedModel):
    optimized_image_fields = ("image",)

    category = models.ForeignKey(
        ServiceCategory,
        verbose_name=_("catégorie"),
        on_delete=models.PROTECT,
        related_name="services",
    )
    slug = models.SlugField(_("identifiant d'URL"), unique=True, max_length=80)
    name = models.CharField(_("nom"), max_length=120)
    description = models.TextField(_("description"), blank=True, max_length=600)
    duration_min = models.PositiveSmallIntegerField(
        _("durée minimale (min)"), validators=[MinValueValidator(5)]
    )
    duration_max = models.PositiveSmallIntegerField(
        _("durée maximale (min)"), null=True, blank=True, help_text=_("Vide si durée fixe.")
    )
    price = models.PositiveIntegerField(
        _("prix (FCFA)"), null=True, blank=True, help_text=_("Vide uniquement si « sur devis ».")
    )
    price_is_from = models.BooleanField(_("prix « dès »"), default=False)
    price_on_quote = models.BooleanField(_("sur devis"), default=False)
    image = models.ImageField(
        _("photo"), upload_to="services", blank=True, validators=[validate_image_upload_size]
    )
    is_active = models.BooleanField(_("visible"), default=True)
    is_popular = models.BooleanField(
        _("tarif populaire"), default=False, help_text=_("Affiché dans « Tarifs populaires ».")
    )

    objects: ClassVar[ServiceManager] = ServiceManager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("prestation")
        verbose_name_plural = _("prestations")
        indexes = [
            models.Index(fields=("category", "is_active", "order")),
            models.Index(
                fields=("order",), condition=Q(is_popular=True), name="service_popular_idx"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(Q(price_on_quote=True, price__isnull=True))
                | (Q(price_on_quote=False, price__isnull=False, price__gt=0)),
                name="service_price_or_quote",
            ),
            models.CheckConstraint(
                condition=Q(duration_max__isnull=True)
                | Q(duration_max__gte=models.F("duration_min")),
                name="service_duration_range",
            ),
            models.CheckConstraint(condition=Q(duration_min__gte=5), name="service_duration_min"),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.price_on_quote and self.price is not None:
            errors["price"] = gettext("Laissez le prix vide pour une prestation sur devis.")
        if not self.price_on_quote and not self.price:
            errors["price"] = gettext("Indiquez un prix, ou cochez « sur devis ».")
        if self.duration_max is not None and self.duration_max < self.duration_min:
            errors["duration_max"] = gettext(
                "La durée maximale doit être supérieure à la minimale."
            )
        if errors:
            raise ValidationError(errors)

    @property
    def longest_duration(self) -> int:
        return self.duration_max or self.duration_min


class Supplement(PublicContent, OrderedModel, TimeStampedModel):
    name = models.CharField(_("nom"), max_length=80)
    price = models.PositiveIntegerField(_("prix (FCFA)"), validators=[MinValueValidator(1)])
    price_is_from = models.BooleanField(_("prix « dès »"), default=False)
    is_active = models.BooleanField(_("visible"), default=True)

    objects: ClassVar[models.Manager[Supplement]] = models.Manager()

    class Meta(OrderedModel.Meta):
        verbose_name = _("supplément")
        verbose_name_plural = _("suppléments")
        constraints = [models.CheckConstraint(condition=Q(price__gt=0), name="supplement_price")]

    def __str__(self) -> str:
        return self.name
