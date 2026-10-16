"""API error handling: DRF errors keep their standard shape, unexpected ones are logged."""

from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("apps.api")


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)
    if response is not None:
        return response
    view = context.get("view")
    logger.exception("Unhandled API error in %s", type(view).__name__ if view else "unknown view")
    return Response({"detail": _("Une erreur interne est survenue. Réessayez plus tard.")}, 500)


def _is_api(request: HttpRequest) -> bool:
    return request.path.startswith("/api/")


def not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    if _is_api(request):
        return JsonResponse({"detail": _("Ressource introuvable.")}, status=404)
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    if _is_api(request):
        return JsonResponse(
            {"detail": _("Une erreur interne est survenue. Réessayez plus tard.")}, status=500
        )
    return render(request, "500.html", status=500)
