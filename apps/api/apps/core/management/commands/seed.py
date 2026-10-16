"""Load the initial Empire T content.

Idempotent and safe to run on every boot: existing rows are left untouched so the owner's
edits in the admin are never overwritten. ``--force`` resets seeded rows to the seed values.
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import models, transaction

from apps.careers.models import JobOpening
from apps.catalog.models import Service, ServiceCategory, Supplement
from apps.core import seed_data as data
from apps.core.models import SiteSettings


def translated(field: str, value: data.T) -> dict[str, str]:
    return {f"{field}_fr": value.fr, f"{field}_en": value.en}


class Command(BaseCommand):
    help = "Load services, prices, supplements, job openings and site settings."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing seeded rows with the seed values (prices included).",
        )

    @transaction.atomic
    def handle(self, *args: Any, force: bool = False, **options: Any) -> None:
        self.force = force
        self.created = 0
        self._seed_catalog()
        self._seed_supplements()
        self._seed_openings()
        self._seed_site_settings()
        mode = "forced" if force else "missing rows only"
        self.stdout.write(self.style.SUCCESS(f"Seed complete ({mode}): {self.created} created."))

    def _upsert(
        self, model: type[models.Model], lookup: dict[str, Any], values: dict[str, Any]
    ) -> Any:
        if self.force:
            obj, created = model._default_manager.update_or_create(**lookup, defaults=values)
        else:
            obj, created = model._default_manager.get_or_create(**lookup, defaults=values)
        self.created += int(created)
        return obj

    def _seed_catalog(self) -> None:
        for category_order, category in enumerate(data.CATEGORIES, start=1):
            category_obj = self._upsert(
                ServiceCategory,
                {"slug": category.slug},
                {
                    **translated("name", category.name),
                    **translated("title", category.title),
                    **translated("tagline", category.tagline),
                    **translated("booking_note", category.booking_note),
                    "accent": category.accent,
                    "appointment_only": category.appointment_only,
                    "show_on_home": category.show_on_home,
                    "order": category_order * 10,
                },
            )
            for service_order, service in enumerate(category.services, start=1):
                duration_min, duration_max = service.duration
                self._upsert(
                    Service,
                    {"slug": service.slug},
                    {
                        "category": category_obj,
                        **translated("name", service.name),
                        **translated("description", service.description),
                        "duration_min": duration_min,
                        "duration_max": duration_max,
                        "price": service.price,
                        "price_is_from": service.from_price,
                        "price_on_quote": service.on_quote,
                        "is_popular": service.popular,
                        "order": service_order * 10,
                    },
                )

    def _seed_supplements(self) -> None:
        for order, supplement in enumerate(data.SUPPLEMENTS, start=1):
            self._upsert(
                Supplement,
                {"name_fr": supplement.name.fr},
                {
                    "name_en": supplement.name.en,
                    "price": supplement.price,
                    "price_is_from": supplement.from_price,
                    "order": order * 10,
                },
            )

    def _seed_openings(self) -> None:
        for order, opening in enumerate(data.OPENINGS, start=1):
            self._upsert(
                JobOpening,
                {"slug": opening.slug},
                {
                    **translated("title", opening.title),
                    **translated("requirements", opening.requirements),
                    "positions_count": opening.positions,
                    "order": order * 10,
                },
            )

    def _seed_site_settings(self) -> None:
        values: dict[str, Any] = dict(data.SITE)
        for field_name, text in data.SITE_TRANSLATED.items():
            values.update(translated(field_name, text))
        values["signature_service"] = Service.objects.get(slug=data.SIGNATURE_SERVICE_SLUG)
        self._upsert(SiteSettings, {"pk": SiteSettings.SINGLETON_PK}, values)
