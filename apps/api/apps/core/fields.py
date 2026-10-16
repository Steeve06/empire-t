"""Serializer building blocks reused by every app (no dependency on other apps)."""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .images import ImageMeta


class ResponsiveImageSchema(serializers.Serializer[Any]):
    src = serializers.URLField()
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
        request = self.context.get("request")

        def absolute(name: str) -> str:
            url = str(storage.url(name))
            if request is not None and url.startswith("/"):
                return str(request.build_absolute_uri(url))
            return url

        variants = meta["variants"]
        return {
            "src": absolute(variants[-1]["name"]),
            "srcset": ", ".join(f"{absolute(v['name'])} {v['width']}w" for v in variants),
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
