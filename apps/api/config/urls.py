from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

admin.site.site_header = "Empire T · Administration"
admin.site.site_title = "Empire T"
admin.site.index_title = "Gestion du salon"

api_v1: list[URLPattern | URLResolver] = [
    path("", include("apps.core.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.bookings.urls")),
    path("", include("apps.careers.urls")),
    path("", include("apps.gallery.urls")),
    path("", include("apps.contact.urls")),
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="v1:schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="v1:schema"), name="redoc"),
]

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1, "api"), namespace="v1")),
]

handler404 = "apps.core.exceptions.not_found"
handler500 = "apps.core.exceptions.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
