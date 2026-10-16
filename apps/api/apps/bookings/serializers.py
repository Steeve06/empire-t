from __future__ import annotations

import datetime as dt
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.catalog.models import Service
from apps.core.fields import HoneypotSerializerMixin
from apps.core.models import SiteSettings
from apps.core.validators import normalize_phone

from .models import BookingChannel, BookingRequest
from .services import available_slots, bookable_dates, shop_whatsapp_url


class BookingCreateSerializer(HoneypotSerializerMixin, serializers.ModelSerializer[BookingRequest]):
    service: serializers.SlugRelatedField[Service] = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Service.objects.active().select_related("category"),
        error_messages={"does_not_exist": _("Cette prestation n'est pas disponible.")},
    )
    time_slot = serializers.TimeField(input_formats=["%H:%M", "%H:%M:%S"])
    customer_name = serializers.CharField(min_length=2, max_length=80, trim_whitespace=True)
    phone = serializers.CharField(max_length=24)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    channel = serializers.ChoiceField(
        choices=[BookingChannel.WEBSITE, BookingChannel.QUICK_BAR],
        default=BookingChannel.WEBSITE,
    )

    class Meta:
        model = BookingRequest
        fields = (
            "service",
            "date",
            "time_slot",
            "customer_name",
            "phone",
            "notes",
            "channel",
            "website",
        )

    def validate_customer_name(self, value: str) -> str:
        # Collapse newlines and runs of spaces: the name is embedded in the WhatsApp message
        return " ".join(value.split())

    def validate_phone(self, value: str) -> str:
        try:
            return normalize_phone(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages[0], code="invalid_phone") from exc

    def validate_date(self, value: dt.date) -> dt.date:
        first, last = bookable_dates(self.context["site"], timezone.localdate())
        if value < first:
            raise serializers.ValidationError(_("Choisissez une date à venir."), code="past")
        if value > last:
            raise serializers.ValidationError(
                _("Les réservations sont ouvertes jusqu'au %(date)s.")
                % {"date": last.strftime("%d/%m/%Y")},
                code="too_far",
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        site: SiteSettings = self.context["site"]
        offered = available_slots(site, attrs["date"], attrs["service"])
        if attrs["time_slot"].replace(second=0, microsecond=0) not in offered:
            raise serializers.ValidationError(
                {"time_slot": _("Ce créneau n'est pas disponible. Choisissez une autre heure.")},
                code="unavailable_slot",
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> BookingRequest:
        service: Service = validated_data["service"]
        return BookingRequest.objects.create(
            **validated_data,
            service_name=service.name,
            price_snapshot=service.price,
            price_is_from=service.price_is_from,
            duration_minutes=service.longest_duration,
            locale=translation.get_language() or "fr",
        )


class BookingCreatedSerializer(serializers.ModelSerializer[BookingRequest]):
    whatsapp_url = serializers.SerializerMethodField(
        help_text="Open this link to send the prefilled request to the shop on WhatsApp."
    )
    service: serializers.SlugRelatedField[Service] = serializers.SlugRelatedField(
        slug_field="slug", read_only=True
    )
    time_slot = serializers.TimeField(format="%H:%M")

    class Meta:
        model = BookingRequest
        fields = (
            "reference",
            "status",
            "service",
            "service_name",
            "date",
            "time_slot",
            "customer_name",
            "whatsapp_url",
        )
        read_only_fields = fields

    def get_whatsapp_url(self, obj: BookingRequest) -> str:
        return shop_whatsapp_url(obj, self.context["site"])


class AvailableSlotsQuerySerializer(serializers.Serializer[Any]):
    date = serializers.DateField()
    service: serializers.SlugRelatedField[Service] = serializers.SlugRelatedField(
        slug_field="slug", queryset=Service.objects.active(), required=False
    )


class AvailableSlotsSerializer(serializers.Serializer[Any]):
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.TimeField(format="%H:%M"))
