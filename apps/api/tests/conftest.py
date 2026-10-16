from __future__ import annotations

import datetime as dt
import io
from collections.abc import Callable, Iterator

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from apps.core.models import SiteSettings


@pytest.fixture(autouse=True)
def _clear_cache() -> Iterator[None]:
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def seeded(db: None) -> SiteSettings:
    """Full seed data with the recruitment deadline moved 30 days into the future."""
    call_command("seed", verbosity=0)
    site = SiteSettings.load()
    site.recruitment_deadline = timezone.localdate() + dt.timedelta(days=30)
    site.save()
    cache.clear()
    return site


@pytest.fixture
def admin_user(db: None) -> User:
    return User.objects.create_superuser("owner", "owner@empire-t.cm", "a-strong-pass-123")


@pytest.fixture
def make_image() -> Callable[..., SimpleUploadedFile]:
    def build(
        width: int = 2000,
        height: int = 1500,
        fmt: str = "JPEG",
        mode: str = "RGB",
        name: str = "photo.jpg",
    ) -> SimpleUploadedFile:
        buffer = io.BytesIO()
        color = (184, 146, 58, 128) if mode == "RGBA" else (184, 146, 58)
        Image.new(mode, (width, height), color).save(buffer, format=fmt)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{fmt.lower()}")

    return build
