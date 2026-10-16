import django_filters

from .models import Service


class ServiceFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__slug", help_text="Category slug, e.g. `men`."
    )
    popular = django_filters.BooleanFilter(
        field_name="is_popular", help_text="Only the services shown in « Tarifs populaires »."
    )

    class Meta:
        model = Service
        fields = ("category", "popular")
