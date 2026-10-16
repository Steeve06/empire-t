from rest_framework import serializers

from apps.catalog.models import Service
from apps.core.fields import ResponsiveImageField

from .models import GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer[GalleryImage]):
    image = ResponsiveImageField("image")
    service: serializers.SlugRelatedField[Service] = serializers.SlugRelatedField(
        slug_field="slug", read_only=True, allow_null=True
    )

    class Meta:
        model = GalleryImage
        fields = ("id", "category", "image", "alt_text", "caption", "service", "is_featured")
