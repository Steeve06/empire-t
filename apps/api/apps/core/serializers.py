"""Serializers for site-wide content."""

from __future__ import annotations

from typing import Any

from django.utils import translation
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.catalog.serializers import ServiceSerializer

from .fields import ResponsiveImageField
from .models import SiteSettings, TeamMember, Testimonial
from .validators import format_cameroon_display
from .whatsapp import whatsapp_link


class TestimonialSerializer(serializers.ModelSerializer[Testimonial]):
    class Meta:
        model = Testimonial
        fields = ("id", "author_name", "author_location", "quote", "rating")


class TeamMemberSerializer(serializers.ModelSerializer[TeamMember]):
    photo = ResponsiveImageField("photo")

    class Meta:
        model = TeamMember
        fields = ("id", "name", "role", "bio", "photo")


class OpeningHoursSerializer(serializers.Serializer[Any]):
    days_label = serializers.CharField()
    opens = serializers.TimeField(format="%H:%M")
    closes = serializers.TimeField(format="%H:%M")
    schema_org = serializers.CharField(help_text="openingHours value for LocalBusiness JSON-LD")


class SocialLinksSerializer(serializers.Serializer[Any]):
    instagram = serializers.URLField(allow_blank=True)
    facebook = serializers.URLField(allow_blank=True)
    tiktok = serializers.URLField(allow_blank=True)


class SiteSettingsSerializer(serializers.ModelSerializer[SiteSettings]):
    whatsapp_display = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()
    opening_hours = serializers.SerializerMethodField()
    social = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    application_documents = serializers.SerializerMethodField()
    recruitment_open = serializers.BooleanField(read_only=True)
    signature_service = serializers.SerializerMethodField()
    hero_image = ResponsiveImageField("hero_image")
    signature_image = ResponsiveImageField("signature_image")
    about_image = ResponsiveImageField("about_image")

    class Meta:
        model = SiteSettings
        fields = (
            "business_name",
            "business_subtitle",
            "tagline",
            "whatsapp_number",
            "whatsapp_display",
            "whatsapp_url",
            "email",
            "address_line",
            "city",
            "country_code",
            "opening_hours",
            "slot_interval_minutes",
            "booking_horizon_days",
            "accepts_mobile_money",
            "social",
            "latitude",
            "longitude",
            "maps_url",
            "recruitment_deadline",
            "recruitment_open",
            "application_documents",
            "story",
            "amenities",
            "signature_service",
            "hero_image",
            "signature_image",
            "about_image",
        )

    def get_whatsapp_display(self, obj: SiteSettings) -> str:
        return format_cameroon_display(obj.whatsapp_number)

    def get_whatsapp_url(self, obj: SiteSettings) -> str:
        greeting = (
            "Hello Empire T, I would like some information."
            if translation.get_language() == "en"
            else "Bonjour Empire T, je souhaite avoir des informations."
        )
        return whatsapp_link(obj.whatsapp_number, greeting)

    @extend_schema_field(OpeningHoursSerializer)
    def get_opening_hours(self, obj: SiteSettings) -> dict[str, str]:
        opens, closes = obj.opening_time.strftime("%H:%M"), obj.closing_time.strftime("%H:%M")
        return {
            "days_label": obj.opening_days_label,
            "opens": opens,
            "closes": closes,
            "schema_org": f"Mo-Su {opens}-{closes}",
        }

    @extend_schema_field(SocialLinksSerializer)
    def get_social(self, obj: SiteSettings) -> dict[str, str]:
        return {
            "instagram": obj.instagram_url,
            "facebook": obj.facebook_url,
            "tiktok": obj.tiktok_url,
        }

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_amenities(self, obj: SiteSettings) -> list[str]:
        return obj.split_lines(obj.amenities)

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_application_documents(self, obj: SiteSettings) -> list[str]:
        return obj.split_lines(obj.application_documents)

    @extend_schema_field(ServiceSerializer(allow_null=True))
    def get_signature_service(self, obj: SiteSettings) -> dict[str, Any] | None:
        service = obj.signature_service
        if service is None or not service.is_active:
            return None
        return ServiceSerializer(service, context=self.context).data
