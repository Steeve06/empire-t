from __future__ import annotations

from django.contrib import admin
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from apps.core.admin_utils import image_preview

from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(TranslationAdmin[GalleryImage]):
    list_display = (
        "thumbnail",
        "alt_text",
        "category",
        "service",
        "is_published",
        "is_featured",
        "order",
    )
    list_display_links = ("thumbnail", "alt_text")
    list_editable = ("category", "is_published", "is_featured", "order")
    list_filter = ("category", "is_published", "is_featured")
    list_select_related = ("service",)
    search_fields = ("alt_text_fr", "alt_text_en", "caption_fr", "caption_en")
    autocomplete_fields = ("service",)
    readonly_fields = ("image_preview",)
    list_per_page = 40
    fieldsets = (
        (None, {"fields": ("image", "image_preview", "category", "alt_text", "caption")}),
        (_("Affichage"), {"fields": ("service", "is_published", "is_featured", "order")}),
    )

    @admin.display(description=_("photo"))
    def thumbnail(self, obj: GalleryImage) -> SafeString:
        return image_preview(obj, "image", 56)

    @admin.display(description=_("aperçu"))
    def image_preview(self, obj: GalleryImage) -> SafeString:
        return image_preview(obj, "image", 220)
