from __future__ import annotations

from django.contrib import admin
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from apps.core.admin_utils import image_preview

from .models import Service, ServiceCategory, Supplement


def format_price(service: Service) -> str:
    if service.price_on_quote or service.price is None:
        return str(_("Sur devis"))
    amount = f"{service.price:,}".replace(",", " ")
    return f"{_('Dès') if service.price_is_from else ''} {amount} F".strip()


def format_duration(service: Service) -> str:
    if service.duration_max and service.duration_max != service.duration_min:
        return f"{service.duration_min} à {service.duration_max} min"
    return f"{service.duration_min} min"


class ServiceInline(TranslationTabularInline[Service, ServiceCategory]):
    model = Service
    extra = 0
    fields = (
        "name",
        "price",
        "price_is_from",
        "price_on_quote",
        "duration_min",
        "duration_max",
        "is_popular",
        "is_active",
        "order",
    )
    show_change_link = True
    ordering = ("order", "id")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TranslationAdmin[ServiceCategory]):
    list_display = ("thumbnail", "title", "slug", "accent", "show_on_home", "is_active", "order")
    list_display_links = ("thumbnail", "title")
    list_editable = ("show_on_home", "is_active", "order")
    list_filter = ("is_active", "accent")
    search_fields = ("name_fr", "name_en", "title_fr", "title_en", "slug")
    prepopulated_fields = {"slug": ("name_fr",)}
    readonly_fields = ("image_preview",)
    inlines = (ServiceInline,)
    fieldsets = (
        (None, {"fields": ("name", "title", "slug", "tagline", "booking_note")}),
        (
            _("Affichage"),
            {"fields": ("accent", "appointment_only", "show_on_home", "is_active", "order")},
        ),
        (_("Photo"), {"fields": ("image", "image_preview")}),
    )

    @admin.display(description=_("photo"))
    def thumbnail(self, obj: ServiceCategory) -> SafeString:
        return image_preview(obj, "image", 40)

    @admin.display(description=_("aperçu"))
    def image_preview(self, obj: ServiceCategory) -> SafeString:
        return image_preview(obj, "image", 160)


@admin.register(Service)
class ServiceAdmin(TranslationAdmin[Service]):
    list_display = (
        "name",
        "category",
        "price_label",
        "price",
        "price_is_from",
        "duration_label",
        "is_popular",
        "is_active",
        "order",
    )
    list_editable = ("price", "price_is_from", "is_popular", "is_active", "order")
    list_filter = ("category", "is_active", "is_popular", "price_on_quote", "price_is_from")
    list_select_related = ("category",)
    search_fields = ("name_fr", "name_en", "slug")
    prepopulated_fields = {"slug": ("name_fr",)}
    readonly_fields = ("image_preview",)
    list_per_page = 50
    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "description")}),
        (_("Prix"), {"fields": ("price", "price_is_from", "price_on_quote")}),
        (_("Durée"), {"fields": ("duration_min", "duration_max")}),
        (_("Affichage"), {"fields": ("is_popular", "is_active", "order")}),
        (_("Photo"), {"fields": ("image", "image_preview")}),
    )

    @admin.display(description=_("tarif affiché"))
    def price_label(self, obj: Service) -> str:
        return format_price(obj)

    @admin.display(description=_("durée"))
    def duration_label(self, obj: Service) -> str:
        return format_duration(obj)

    @admin.display(description=_("aperçu"))
    def image_preview(self, obj: Service) -> SafeString:
        return image_preview(obj, "image", 160)


@admin.register(Supplement)
class SupplementAdmin(TranslationAdmin[Supplement]):
    list_display = ("name", "price", "price_is_from", "is_active", "order")
    list_editable = ("price", "price_is_from", "is_active", "order")
    search_fields = ("name_fr", "name_en")
