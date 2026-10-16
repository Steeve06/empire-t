from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache
from django.db import DatabaseError, connection
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import CachedListMixin, cached_api_response
from .models import SiteSettings, TeamMember, Testimonial
from .serializers import SiteSettingsSerializer, TeamMemberSerializer, TestimonialSerializer

logger = logging.getLogger(__name__)

LANG_PARAMETER = OpenApiParameter(
    "lang", str, enum=["fr", "en"], description="Content language (defaults to French)."
)


def require_site_settings() -> SiteSettings:
    """The singleton, or a 404 with a clear log line when the database was never seeded."""
    try:
        return SiteSettings.load()
    except SiteSettings.DoesNotExist as exc:
        logger.error("SiteSettings missing: run `manage.py seed`")
        raise NotFound(_("Paramètres du site non configurés.")) from exc


@extend_schema(parameters=[LANG_PARAMETER], responses=SiteSettingsSerializer)
class SiteSettingsView(APIView):
    """Shop details, hours, social links, images and recruitment status."""

    def get(self, request: Request) -> Response:
        return cached_api_response(request, lambda: self._build(request))

    def _build(self, request: Request) -> Response:
        site = require_site_settings()
        return Response(SiteSettingsSerializer(site, context={"request": request}).data)


@extend_schema(parameters=[LANG_PARAMETER])
class TestimonialListView(CachedListMixin, generics.ListAPIView[Testimonial]):
    serializer_class = TestimonialSerializer
    pagination_class = None
    queryset = Testimonial.objects.filter(is_published=True)


@extend_schema(parameters=[LANG_PARAMETER])
class TeamMemberListView(CachedListMixin, generics.ListAPIView[TeamMember]):
    serializer_class = TeamMemberSerializer
    pagination_class = None
    queryset = TeamMember.objects.filter(is_active=True)


class HealthView(APIView):
    """Liveness and readiness probe used by Docker and the load balancer."""

    throttle_classes = ()

    @extend_schema(
        responses={
            200: inline_serializer(
                "Health", {"database": serializers.CharField(), "cache": serializers.CharField()}
            )
        }
    )
    def get(self, request: Request) -> Response:
        checks: dict[str, Any] = {"database": "ok", "cache": "ok"}
        healthy = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError:
            logger.exception("Health check: database unreachable")
            checks["database"] = "error"
            healthy = False
        cache.set("health:ping", "pong", 5)
        if cache.get("health:ping") != "pong":
            checks["cache"] = "degraded"
        response = Response(
            checks, status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        response["Cache-Control"] = "no-store"
        return response
