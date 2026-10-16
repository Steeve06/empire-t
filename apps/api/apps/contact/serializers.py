from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import translation
from rest_framework import serializers

from apps.core.fields import HoneypotSerializerMixin
from apps.core.validators import normalize_contact

from .models import ContactMessage


class ContactMessageCreateSerializer(
    HoneypotSerializerMixin, serializers.ModelSerializer[ContactMessage]
):
    name = serializers.CharField(min_length=2, max_length=80)
    contact = serializers.CharField(max_length=254)
    message = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = ContactMessage
        fields = ("name", "contact", "message", "website")

    def validate_name(self, value: str) -> str:
        return " ".join(value.split())

    def validate_contact(self, value: str) -> str:
        try:
            normalized, kind = normalize_contact(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages[0], code="invalid_contact") from exc
        self._contact_kind = kind
        return normalized

    def create(self, validated_data: dict[str, Any]) -> ContactMessage:
        return ContactMessage.objects.create(
            **validated_data,
            contact_kind=self._contact_kind,
            locale=translation.get_language() or "fr",
        )


class ContactReceivedSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
