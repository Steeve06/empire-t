from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("categories", views.ServiceCategoryViewSet, basename="category")
router.register("services", views.ServiceViewSet, basename="service")

urlpatterns = [
    path("supplements/", views.SupplementListView.as_view(), name="supplement-list"),
    path("", include(router.urls)),
]
