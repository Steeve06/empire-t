from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import translation

SUPPORTED_LANGUAGES = frozenset(code for code, _ in settings.LANGUAGES)


class QueryLanguageMiddleware:
    """``?lang=en`` wins over Accept-Language, so CDN and nginx cache keys stay URL-based."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        lang = request.GET.get("lang")
        if lang in SUPPORTED_LANGUAGES:
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        return self.get_response(request)
