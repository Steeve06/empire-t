"""Read-through cache for public API responses.

Keys carry a global *content version*. Any save or delete of a ``PublicContent`` model bumps
that version, so every cached response becomes unreachable at once and expires on its own.
Content changes a few times a week at most, so global invalidation is simpler and safer than
tracking which endpoint depends on which model (see docs/decisions.md, ADR-006).
Keys also carry the local date (date-dependent fields such as ``recruitment_open`` roll over
at midnight) and the active language.
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import Model
from django.utils import timezone, translation
from django.utils.cache import patch_cache_control, patch_vary_headers
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger(__name__)

CONTENT_VERSION_KEY = "api:content-version"


def content_version() -> int:
    version = cache.get(CONTENT_VERSION_KEY)
    if version is None:
        cache.add(CONTENT_VERSION_KEY, 1, timeout=None)
        version = cache.get(CONTENT_VERSION_KEY, 1)
    return int(version)


def bump_content_version() -> None:
    try:
        cache.incr(CONTENT_VERSION_KEY)
    except ValueError:
        cache.set(CONTENT_VERSION_KEY, content_version() + 1, timeout=None)


def response_cache_key(request: Request) -> str:
    path_hash = hashlib.sha256(request.get_full_path().encode()).hexdigest()[:32]
    return ":".join(
        (
            "api",
            str(content_version()),
            timezone.localdate().isoformat(),
            translation.get_language() or settings.LANGUAGE_CODE,
            path_hash,
        )
    )


def cached_api_response(request: Request, produce: Callable[[], Response]) -> Response:
    """Serve ``produce()``'s data from cache when possible and add HTTP cache headers."""
    key = response_cache_key(request)
    data = cache.get(key)
    if data is None:
        response = produce()
        if response.status_code == 200:
            cache.set(key, response.data, settings.API_CACHE_TIMEOUT)
        response["X-Cache"] = "MISS"
    else:
        response = Response(data)
        response["X-Cache"] = "HIT"
    if response.status_code == 200:
        patch_cache_control(
            response,
            public=True,
            max_age=settings.API_HTTP_MAX_AGE,
            stale_while_revalidate=settings.API_HTTP_MAX_AGE * 10,
        )
    patch_vary_headers(response, ("Accept-Language",))
    return response


class CachedListMixin(ListModelMixin):
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        uncached = super().list
        return cached_api_response(request, lambda: uncached(request, *args, **kwargs))


class CachedRetrieveMixin(RetrieveModelMixin):
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        uncached = super().retrieve
        return cached_api_response(request, lambda: uncached(request, *args, **kwargs))


def invalidate_on_content_change(sender: type[Model], **_: Any) -> None:
    """Signal receiver connected in ``CoreConfig.ready`` for post_save and post_delete."""
    if getattr(sender, "invalidates_api_cache", False):
        logger.debug("Content changed (%s): bumping API cache version", sender.__name__)
        bump_content_version()
