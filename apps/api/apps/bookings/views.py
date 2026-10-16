from __future__ import annotations

import logging
from typing import Any

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.models import SiteSettings
from apps.core.views import LANG_PARAMETER, require_site_settings

from .models import BookingRequest
from .serializers import (
    AvailableSlotsQuerySerializer,
    AvailableSlotsSerializer,
    BookingCreatedSerializer,
    BookingCreateSerializer,
)
from .services import available_slots

logger = logging.getLogger(__name__)


@extend_schema(
    parameters=[LANG_PARAMETER],
    request=BookingCreateSerializer,
    responses={201: BookingCreatedSerializer},
)
class BookingCreateView(generics.CreateAPIView[BookingRequest]):
    """Store a booking request and return the prefilled WhatsApp link to the shop."""

    serializer_class = BookingCreateSerializer
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "bookings"
    site: SiteSettings

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "site": self.site}

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.site = require_site_settings()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        logger.info("Booking request %s created (%s)", booking.reference, booking.service_name)
        data = BookingCreatedSerializer(booking, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)


class AvailableSlotsView(APIView):
    """Start times that can be requested for a date (and optionally a service)."""

    @extend_schema(
        parameters=[
            OpenApiParameter("date", str, required=True, description="YYYY-MM-DD"),
            OpenApiParameter("service", str, required=False, description="Service slug"),
        ],
        responses=AvailableSlotsSerializer,
    )
    def get(self, request: Request) -> Response:
        query = AvailableSlotsQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        day = query.validated_data["date"]
        slots = available_slots(require_site_settings(), day, query.validated_data.get("service"))
        response = Response(AvailableSlotsSerializer({"date": day, "slots": slots}).data)
        response["Cache-Control"] = "private, max-age=60"
        return response
