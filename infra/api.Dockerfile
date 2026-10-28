# Multi-stage image for the Django API.
#   target "dev"  : dev dependencies, runserver with autoreload, source bind-mounted by compose
#   target "prod" : slim runtime, gunicorn, non-root user, static files collected at build time

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN groupadd --system app && useradd --system --gid app --home /app --shell /usr/sbin/nologin app
WORKDIR /app

# ---- Build wheels once so runtime stages never need compilers -------------
FROM base AS wheels
COPY apps/api/requirements/ /req/
RUN pip wheel --wheel-dir /wheels -r /req/dev.txt

# ---- Development -----------------------------------------------------------
FROM base AS dev
# gettext provides msgfmt for `make messages` (compiling the English API messages)
RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*
COPY --from=wheels /wheels /wheels
COPY apps/api/requirements/ /req/
RUN pip install --no-index --find-links /wheels -r /req/dev.txt && rm -rf /wheels
COPY --chown=app:app apps/api/ /app/
RUN mkdir -p /app/media /app/private_media /api-client && chown -R app:app /app /api-client
USER app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- Production ------------------------------------------------------------
FROM base AS prod
COPY --from=wheels /wheels /wheels
COPY apps/api/requirements/base.txt /req/base.txt
RUN pip install --no-index --find-links /wheels -r /req/base.txt && rm -rf /wheels /req
COPY --chown=app:app apps/api/ /app/
# collectstatic needs settings but no real secrets or database
RUN DJANGO_SETTINGS_MODULE=config.settings.prod \
    DJANGO_SECRET_KEY=build-only \
    DATABASE_URL=sqlite:////tmp/build.db \
    DJANGO_ALLOWED_HOSTS=build \
    python manage.py collectstatic --noinput \
 && mkdir -p /app/media /app/private_media \
 && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/', timeout=4).status == 200 else 1)"
CMD ["gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py"]
