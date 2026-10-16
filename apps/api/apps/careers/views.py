from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.core.cache import CachedListMixin
from apps.core.models import SiteSettings
from apps.core.notifications import admin_change_url, notify_shop_on_commit
from apps.core.views import LANG_PARAMETER, require_site_settings

from .models import JobApplication, JobOpening
from .serializers import (
    ApplicationReceivedSerializer,
    JobApplicationCreateSerializer,
    JobOpeningSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(parameters=[LANG_PARAMETER])
class JobOpeningListView(CachedListMixin, generics.ListAPIView[JobOpening]):
    """Open positions. Empty once the recruitment deadline has passed."""

    serializer_class = JobOpeningSerializer
    pagination_class = None
    site: SiteSettings

    def get_queryset(self) -> QuerySet[JobOpening]:
        if getattr(self, "swagger_fake_view", False):  # schema generation, no request data
            return JobOpening.objects.none()
        self.site = require_site_settings()
        return JobOpening.objects.open_on(timezone.localdate(), self.site)

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "site": self.site}


@extend_schema(
    parameters=[LANG_PARAMETER],
    request={"multipart/form-data": JobApplicationCreateSerializer},
    responses={201: ApplicationReceivedSerializer},
)
class JobApplicationCreateView(generics.CreateAPIView[JobApplication]):
    """Multipart upload: fields plus one or more `files` parts."""

    serializer_class = JobApplicationCreateSerializer
    parser_classes = (MultiPartParser,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "applications"

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "site": require_site_settings()}

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        files = list(application.files.all())
        logger.info("Job application %s received (%d files)", application.pk, len(files))
        with translation.override("fr"):
            subject = (
                f"Nouvelle candidature : {application.opening.title} - {application.full_name}"
            )
        notify_shop_on_commit(
            subject,
            "emails/new_application.txt",
            {
                "application": application,
                "files": files,
                "admin_url": admin_change_url("careers", "jobapplication", application.pk),
            },
        )
        return Response(
            {"detail": _("Candidature envoyée. Nous vous contacterons très bientôt.")},
            status=status.HTTP_201_CREATED,
        )
