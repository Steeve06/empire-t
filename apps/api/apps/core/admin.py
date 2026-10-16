from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .admin_utils import image_preview
from .models import SiteSettings, TeamMember, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin[SiteSettings]):
    """Singleton: the list page jumps straight to the edit form."""

    autocomplete_fields = ("signature_service",)
    # The owner may paste "instagram.com/empire_t": complete it to https://, not http://
    formfield_overrides = {models.URLField: {"assume_scheme": "https"}}
    readonly_fields = ("hero_preview", "signature_preview", "about_preview", "updated_at")
    fieldsets = (
        (_("Identité"), {"fields": ("business_name", "business_subtitle", "tagline")}),
        (
            _("Contact"),
            {"fields": ("whatsapp_number", "email", "notification_email", "accepts_mobile_money")},
        ),
        (
            _("Adresse et carte"),
            {
                "fields": (
                    "address_line",
                    "city",
                    "country_code",
                    "latitude",
                    "longitude",
                    "maps_url",
                )
            },
        ),
        (
            _("Horaires et réservations"),
            {
                "fields": (
                    "opening_days_label",
                    "opening_time",
                    "closing_time",
                    "slot_interval_minutes",
                    "booking_lead_minutes",
                    "booking_horizon_days",
                )
            },
        ),
        (_("Réseaux sociaux"), {"fields": ("instagram_url", "facebook_url", "tiktok_url")}),
        (_("Recrutement"), {"fields": ("recruitment_deadline", "application_documents")}),
        (_("Page À propos"), {"fields": ("story", "amenities")}),
        (
            _("Photos et forfait signature"),
            {
                "fields": (
                    "signature_service",
                    ("hero_image", "hero_preview"),
                    ("signature_image", "signature_preview"),
                    ("about_image", "about_preview"),
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description=_("aperçu"))
    def hero_preview(self, obj: SiteSettings) -> SafeString:
        return image_preview(obj, "hero_image", 96)

    @admin.display(description=_("aperçu"))
    def signature_preview(self, obj: SiteSettings) -> SafeString:
        return image_preview(obj, "signature_image", 96)

    @admin.display(description=_("aperçu"))
    def about_preview(self, obj: SiteSettings) -> SafeString:
        return image_preview(obj, "about_image", 96)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        if SiteSettings.objects.exists():
            return HttpResponseRedirect(
                reverse("admin:core_sitesettings_change", args=[SiteSettings.SINGLETON_PK])
            )
        return super().changelist_view(request, extra_context)


@admin.register(Testimonial)
class TestimonialAdmin(TranslationAdmin[Testimonial]):
    list_display = ("author_name", "author_location", "rating", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("is_published", "rating")
    search_fields = ("author_name", "quote_fr", "quote_en")


@admin.register(TeamMember)
class TeamMemberAdmin(TranslationAdmin[TeamMember]):
    list_display = ("thumbnail", "name", "role", "is_active", "order")
    list_display_links = ("thumbnail", "name")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "role_fr", "role_en")
    readonly_fields = ("photo_preview",)

    @admin.display(description=_("photo"))
    def thumbnail(self, obj: TeamMember) -> SafeString:
        return image_preview(obj, "photo", 48)

    @admin.display(description=_("aperçu"))
    def photo_preview(self, obj: TeamMember) -> SafeString:
        return image_preview(obj, "photo", 160)
