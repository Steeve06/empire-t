from __future__ import annotations

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets

from apps.core.cache import CachedListMixin, CachedRetrieveMixin
from apps.core.views import LANG_PARAMETER

from .filters import ServiceFilter
from .models import Service, ServiceCategory, Supplement
from .serializers import ServiceCategorySerializer, ServiceSerializer, SupplementSerializer


@extend_schema_view(
    list=extend_schema(parameters=[LANG_PARAMETER]),
    retrieve=extend_schema(parameters=[LANG_PARAMETER]),
)
class ServiceCategoryViewSet(
    CachedListMixin, CachedRetrieveMixin, viewsets.GenericViewSet[ServiceCategory]
):
    """Categories with their active services and starting price (the full price menu)."""

    serializer_class = ServiceCategorySerializer
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self) -> QuerySet[ServiceCategory]:
        return ServiceCategory.objects.with_active_services()


@extend_schema_view(
    list=extend_schema(parameters=[LANG_PARAMETER]),
    retrieve=extend_schema(parameters=[LANG_PARAMETER]),
)
class ServiceViewSet(CachedListMixin, CachedRetrieveMixin, viewsets.GenericViewSet[Service]):
    """Active services, filterable by category slug and popularity."""

    serializer_class = ServiceSerializer
    lookup_field = "slug"
    filterset_class = ServiceFilter

    def get_queryset(self) -> QuerySet[Service]:
        return (
            Service.objects.active()
            .select_related("category")
            .order_by("category__order", "order", "id")
        )


@extend_schema(parameters=[LANG_PARAMETER])
class SupplementListView(CachedListMixin, generics.ListAPIView[Supplement]):
    serializer_class = SupplementSerializer
    pagination_class = None
    queryset = Supplement.objects.filter(is_active=True)
