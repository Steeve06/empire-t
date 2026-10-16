from __future__ import annotations

import logging
from typing import Any

from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.core.notifications import admin_change_url, notify_shop_on_commit
from apps.core.views import LANG_PARAMETER

from .models import ContactMessage
from .serializers import ContactMessageCreateSerializer, ContactReceivedSerializer

logger = logging.getLogger(__name__)


@extend_schema(parameters=[LANG_PARAMETER], responses={201: ContactReceivedSerializer})
class ContactMessageCreateView(generics.CreateAPIView[ContactMessage]):
    serializer_class = ContactMessageCreateSerializer
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "contact"

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        logger.info("Contact message %s received", message.pk)
        notify_shop_on_commit(
            f"Nouveau message du site : {message.name}",
            "emails/new_contact_message.txt",
            {
                "message": message,
                "admin_url": admin_change_url("contact", "contactmessage", message.pk),
            },
        )
        return Response(
            {"detail": _("Merci ! Votre message a bien été envoyé. Nous vous répondons vite.")},
            status=status.HTTP_201_CREATED,
        )
