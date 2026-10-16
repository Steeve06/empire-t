from __future__ import annotations

import django_filters
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.core.cache import CachedListMixin
from apps.core.views import LANG_PARAMETER

from .models import GalleryCategory, GalleryImage
from .serializers import GalleryImageSerializer


class GalleryFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=GalleryCategory.choices)
    featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = GalleryImage
        fields = ("category", "featured")


@extend_schema(parameters=[LANG_PARAMETER])
class GalleryImageListView(CachedListMixin, generics.ListAPIView[GalleryImage]):
    """Published photos in display order. Filter with `category` and `featured`."""

    serializer_class = GalleryImageSerializer
    filterset_class = GalleryFilter

    def get_queryset(self) -> QuerySet[GalleryImage]:
        # Only images with processed variants are exposed (no broken <img> on the site)
        return (
            GalleryImage.objects.filter(is_published=True)
            .exclude(image_meta={})
            .select_related("service")
        )
