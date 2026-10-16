from __future__ import annotations

from rest_framework import serializers

from apps.core.fields import ResponsiveImageField

from .models import Service, ServiceCategory, Supplement


class ServiceSerializer(serializers.ModelSerializer[Service]):
    category: serializers.SlugRelatedField[ServiceCategory] = serializers.SlugRelatedField(
        slug_field="slug", read_only=True
    )
    image = ResponsiveImageField("image")

    class Meta:
        model = Service
        fields: tuple[str, ...] = (
            "id",
            "slug",
            "category",
            "name",
            "description",
            "duration_min",
            "duration_max",
            "price",
            "price_is_from",
            "price_on_quote",
            "is_popular",
            "image",
        )


class ServiceInCategorySerializer(ServiceSerializer):
    """Nested in a category: the category is implied, so skip it (and its query)."""

    class Meta(ServiceSerializer.Meta):
        fields = tuple(f for f in ServiceSerializer.Meta.fields if f != "category")


class ServiceCategorySerializer(serializers.ModelSerializer[ServiceCategory]):
    starting_price = serializers.IntegerField(read_only=True, allow_null=True)
    # Always read through ServiceCategory.objects.with_active_services() (prefetched, no N+1)
    services = ServiceInCategorySerializer(many=True, read_only=True, source="active_services")
    image = ResponsiveImageField("image")

    class Meta:
        model = ServiceCategory
        fields = (
            "id",
            "slug",
            "name",
            "title",
            "tagline",
            "booking_note",
            "accent",
            "appointment_only",
            "show_on_home",
            "starting_price",
            "image",
            "services",
        )


class SupplementSerializer(serializers.ModelSerializer[Supplement]):
    class Meta:
        model = Supplement
        fields = ("id", "name", "price", "price_is_from")
