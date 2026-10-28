"""Serializer building blocks reused by every app (no dependency on other apps)."""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .images import ImageMeta


class ResponsiveImageSchema(serializers.Serializer[Any]):
    src = serializers.CharField(help_text="Largest variant; root-relative or absolute.")
    srcset = serializers.CharField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()


@extend_schema_field(ResponsiveImageSchema(allow_null=True))
class ResponsiveImageField(serializers.Field):  # type: ignore[type-arg]
    """Exposes an ``OptimizedImagesModel`` image as ``{src, srcset, width, height}`` or null."""

    def __init__(self, image_field: str, **kwargs: Any) -> None:
        self.image_field = image_field
        kwargs.update(source="*", read_only=True)
        super().__init__(**kwargs)

    def to_representation(self, instance: Any) -> dict[str, Any] | None:
        meta: ImageMeta | None = instance.image_meta.get(self.image_field)
        if not meta:
            return None
        storage = getattr(instance, self.image_field).storage
        # Storage URLs as-is: root-relative locally (same origin behind nginx and the Vite
        # proxy), absolute on S3. Never derived from the Host header, so cached responses
        # are identical for every client, including the build-time pre-renderer.
        variants = meta["variants"]
        return {
            "src": str(storage.url(variants[-1]["name"])),
            "srcset": ", ".join(f"{storage.url(v['name'])} {v['width']}w" for v in variants),
            "width": meta["width"],
            "height": meta["height"],
        }


class HoneypotSerializerMixin(serializers.Serializer[Any]):
    """Hidden ``website`` field: humans never see it, naive bots fill it in."""

    website = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        max_length=200,
        help_text="Anti-spam trap. Must stay empty.",
    )

    def validate_website(self, value: str) -> str:
        if value:
            raise serializers.ValidationError(_("Envoi refusé."), code="spam")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs.pop("website", None)
        validated: dict[str, Any] = super().validate(attrs)
        return validated
