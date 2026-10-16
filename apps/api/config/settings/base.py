"""Settings shared by every environment. Environment-specific modules override these."""

from pathlib import Path
from typing import Any

import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR.parent.parent / ".env", overwrite=False)

SECRET_KEY: str = env("DJANGO_SECRET_KEY")
DEBUG: bool = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS: list[str] = env.list("DJANGO_ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    # modeltranslation must come before django.contrib.admin
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "apps.core",
    "apps.catalog",
    "apps.bookings",
    "apps.careers",
    "apps.gallery",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "apps.core.middleware.QueryLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # A cache outage must degrade to "uncached", never to a 500
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "empire",
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation -------------------------------------------------------
LANGUAGE_CODE = "fr"
LANGUAGES = [("fr", _("Français")), ("en", _("English"))]
MODELTRANSLATION_DEFAULT_LANGUAGE = "fr"
MODELTRANSLATION_FALLBACK_LANGUAGES = ("fr",)
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

# --- Static and media -----------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
PRIVATE_MEDIA_ROOT = BASE_DIR / "private_media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Job application documents: never served publicly, downloaded through the admin
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": str(PRIVATE_MEDIA_ROOT), "base_url": None},
    },
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 10

# --- Django REST Framework ------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "240/minute",
        "bookings": "10/hour",
        "applications": "5/hour",
        "contact": "5/hour",
    },
    "NUM_PROXIES": env.int("NUM_PROXIES", default=0),
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Empire T Barbershop & Beauty API",
    "DESCRIPTION": (
        "Public API for the Empire T website. Read endpoints are cached; write endpoints are "
        "throttled. Send `?lang=fr` or `?lang=en` (or Accept-Language) to choose the content "
        "language."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "BookingStatusEnum": "apps.bookings.models.BookingStatus",
        "GalleryCategoryEnum": "apps.gallery.models.GalleryCategory",
    },
}

# --- CORS / CSRF ----------------------------------------------------------------
CORS_ALLOWED_ORIGINS: list[str] = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_CREDENTIALS = False
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# --- Security defaults (hardened further in prod) ---------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# --- Email ------------------------------------------------------------------------
vars().update(env.email_url("EMAIL_URL", default="consolemail://"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Empire T <no-reply@empire-t.cm>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 15

# --- Domain configuration ---------------------------------------------------------
API_CACHE_TIMEOUT = env.int("API_CACHE_TIMEOUT", default=60 * 60)
API_HTTP_MAX_AGE = env.int("API_HTTP_MAX_AGE", default=60)
ADMIN_URL_BASE = env("ADMIN_URL_BASE", default="http://localhost:8000")

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": env("APP_LOG_LEVEL", default="INFO")},
    },
}
