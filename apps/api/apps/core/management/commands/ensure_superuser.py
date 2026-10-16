"""Create the admin account from DJANGO_SUPERUSER_* variables if it does not exist yet."""

from __future__ import annotations

import os
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Idempotently create the superuser from DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD."

    def handle(self, *args: Any, **options: Any) -> None:
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not set: skipped. "
                    "Use `python manage.py createsuperuser` instead."
                )
            )
            return

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists: nothing to do.")
            return

        candidate = user_model(username=username, email=email)
        try:
            validate_password(password, candidate)
        except ValidationError as exc:
            raise CommandError("Weak DJANGO_SUPERUSER_PASSWORD: " + " ".join(exc.messages)) from exc

        user_model.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
