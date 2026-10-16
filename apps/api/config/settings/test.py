"""Test settings: real Postgres (as in production), in-memory cache and email, temp media."""

import tempfile
from pathlib import Path

from .base import *

DEBUG = False
SECRET_KEY = "test-only-secret-key"  # noqa: S105
ALLOWED_HOSTS = ["testserver", "localhost"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "empire-tests",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

_media_tmp = Path(tempfile.mkdtemp(prefix="empire-media-"))
STATIC_ROOT = _media_tmp / "static"
STATIC_ROOT.mkdir()
MEDIA_ROOT = _media_tmp / "public"
PRIVATE_MEDIA_ROOT = _media_tmp / "private"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": str(PRIVATE_MEDIA_ROOT), "base_url": None},
    },
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

LOGGING["root"]["level"] = "WARNING"
