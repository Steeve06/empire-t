"""Production settings: HTTPS only, hardened cookies, optional S3-compatible media."""

from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
NUM_PROXIES = env.int("NUM_PROXIES", default=1)
REST_FRAMEWORK["NUM_PROXIES"] = NUM_PROXIES

# HTTPS: nginx terminates TLS and forwards the original scheme
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health/$"]
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# S3-compatible object storage (AWS S3, Cloudflare R2, Backblaze B2, DigitalOcean Spaces...)
if env.bool("USE_S3", default=False):
    _s3_common = {
        "access_key": env("S3_ACCESS_KEY_ID"),
        "secret_key": env("S3_SECRET_ACCESS_KEY"),
        "bucket_name": env("S3_BUCKET_NAME"),
        "endpoint_url": env("S3_ENDPOINT_URL", default=None),
        "region_name": env("S3_REGION_NAME", default=None),
        "file_overwrite": False,
    }
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **_s3_common,
            "location": "media",
            "querystring_auth": False,
            "custom_domain": env("S3_CUSTOM_DOMAIN", default=None),
            "object_parameters": {"CacheControl": "public, max-age=2592000"},
        },
    }
    STORAGES["private"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **_s3_common,
            "location": "private",
            "default_acl": "private",
            "querystring_auth": True,
            "querystring_expire": 300,
        },
    }

LOGGING["root"]["level"] = env("LOG_LEVEL", default="INFO")
ADMINS = [("Empire T", email) for email in env.list("DJANGO_ADMINS_EMAILS", default=[])]
