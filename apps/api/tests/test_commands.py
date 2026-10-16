from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.careers.models import JobOpening
from apps.catalog.models import Service, ServiceCategory, Supplement
from apps.core.models import SiteSettings

pytestmark = pytest.mark.django_db


def run(*args: str) -> str:
    out = StringIO()
    call_command(*args, stdout=out)
    return out.getvalue()


def test_seed_loads_everything_once() -> None:
    assert "37 created" in run("seed")
    assert ServiceCategory.objects.count() == 5
    assert Service.objects.count() == 23
    assert Supplement.objects.count() == 4
    assert JobOpening.objects.count() == 4
    site = SiteSettings.load()
    assert site.signature_service is not None
    assert site.signature_service.slug == "empire-premium"
    assert site.whatsapp_number == "+237653147512"

    assert "0 created" in run("seed")
    assert Service.objects.count() == 23


def test_seed_never_overwrites_owner_edits() -> None:
    run("seed")
    Service.objects.filter(slug="skin-fade").update(price=2500)
    run("seed")
    assert Service.objects.get(slug="skin-fade").price == 2500


def test_seed_force_restores_seed_values() -> None:
    run("seed")
    Service.objects.filter(slug="skin-fade").update(price=2500)
    assert "forced" in run("seed", "--force")
    assert Service.objects.get(slug="skin-fade").price == 2000


def test_every_seeded_text_has_an_english_translation() -> None:
    run("seed")
    # *_en columns are added at runtime by modeltranslation, hence getattr
    checks = [
        (Service.objects.all(), ("name_en",)),
        (ServiceCategory.objects.all(), ("name_en", "title_en", "tagline_en")),
        (Supplement.objects.all(), ("name_en",)),
        (JobOpening.objects.all(), ("title_en", "requirements_en")),
        (SiteSettings.objects.all(), ("tagline_en", "story_en", "amenities_en")),
    ]
    for queryset, fields in checks:
        for obj in queryset:
            for field in fields:
                assert getattr(obj, field), f"{obj!r} missing {field}"


def test_ensure_superuser_skips_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    assert "skipped" in run("ensure_superuser")
    assert not User.objects.exists()


def test_ensure_superuser_is_idempotent(monkeypatch) -> None:
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "patron")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "patron@empire-t.cm")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "Empire-T-2026!")
    assert "created" in run("ensure_superuser")
    assert "already exists" in run("ensure_superuser")
    user = User.objects.get()
    assert user.is_superuser and user.check_password("Empire-T-2026!")


def test_ensure_superuser_rejects_weak_password(monkeypatch) -> None:
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "patron")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "1234")
    with pytest.raises(CommandError):
        run("ensure_superuser")
