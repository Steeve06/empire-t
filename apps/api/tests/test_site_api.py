import datetime as dt
from urllib.parse import unquote

import pytest
from django.db import DatabaseError
from django.utils import timezone

from apps.core.models import SiteSettings, TeamMember, Testimonial

pytestmark = pytest.mark.django_db

SITE_URL = "/api/v1/site/"


def test_site_settings_payload(api, seeded) -> None:
    data = api.get(SITE_URL).json()

    assert data["business_name"] == "Empire T"
    assert data["tagline"] == "Plus qu'une coupe, une expérience."
    assert data["whatsapp_number"] == "+237653147512"
    assert data["whatsapp_display"] == "653 147 512"
    assert data["whatsapp_url"].startswith("https://wa.me/237653147512?text=Bonjour")
    assert data["opening_hours"] == {
        "days_label": "Ouvert 7j/7",
        "opens": "07:00",
        "closes": "21:00",
        "schema_org": "Mo-Su 07:00-21:00",
    }
    assert data["accepts_mobile_money"] is True
    assert "Wi-Fi gratuit" in data["amenities"]
    assert data["application_documents"][0] == "Lettre de motivation"
    assert data["recruitment_open"] is True
    assert data["signature_service"]["slug"] == "empire-premium"
    assert data["signature_service"]["price"] == 3500
    assert data["hero_image"] is None
    assert set(data["social"]) == {"instagram", "facebook", "tiktok"}


def test_site_settings_in_english(api, seeded) -> None:
    data = api.get(SITE_URL, {"lang": "en"}).json()
    assert data["tagline"] == "More than a haircut, an experience."
    assert data["opening_hours"]["days_label"] == "Open 7 days a week"
    assert "Hello" in unquote(data["whatsapp_url"])
    assert data["signature_service"]["description"].startswith("Haircut, beard trim")


def test_accept_language_header_selects_english(api, seeded) -> None:
    data = api.get(SITE_URL, HTTP_ACCEPT_LANGUAGE="en-GB,en;q=0.9").json()
    assert data["tagline"] == "More than a haircut, an experience."


def test_unknown_lang_falls_back_to_french(api, seeded) -> None:
    assert api.get(SITE_URL, {"lang": "de"}).json()["tagline"].startswith("Plus")


def test_recruitment_closes_after_deadline(api, seeded) -> None:
    seeded.recruitment_deadline = timezone.localdate() - dt.timedelta(days=1)
    seeded.save()
    assert api.get(SITE_URL).json()["recruitment_open"] is False


def test_recruitment_open_on_deadline_day(seeded) -> None:
    seeded.recruitment_deadline = timezone.localdate()
    assert seeded.recruitment_open is True


def test_inactive_signature_service_is_hidden(api, seeded) -> None:
    service = seeded.signature_service
    service.is_active = False
    service.save()
    assert api.get(SITE_URL).json()["signature_service"] is None


def test_missing_settings_returns_404(api, db) -> None:
    response = api.get(SITE_URL)
    assert response.status_code == 404
    assert "detail" in response.json()


def test_singleton_is_forced_to_pk_1(seeded) -> None:
    seeded.pk = 99
    seeded.save()
    assert SiteSettings.objects.count() == 1
    assert SiteSettings.objects.get().pk == 1


def test_reads_are_cached_and_invalidated_on_save(api, seeded) -> None:
    first = api.get(SITE_URL)
    second = api.get(SITE_URL)
    assert first["X-Cache"] == "MISS"
    assert second["X-Cache"] == "HIT"
    assert "max-age=60" in second["Cache-Control"]
    assert "public" in second["Cache-Control"]
    assert "Accept-Language" in second["Vary"]

    seeded.tagline_fr = "Nouveau slogan"
    seeded.save()

    third = api.get(SITE_URL)
    assert third["X-Cache"] == "MISS"
    assert third.json()["tagline"] == "Nouveau slogan"


def test_cache_is_separate_per_language(api, seeded) -> None:
    assert api.get(SITE_URL, {"lang": "fr"}).json()["tagline"].startswith("Plus")
    assert api.get(SITE_URL, {"lang": "en"}).json()["tagline"].startswith("More")


def test_cached_read_runs_no_queries(api, seeded, django_assert_num_queries) -> None:
    api.get(SITE_URL)
    with django_assert_num_queries(0):
        assert api.get(SITE_URL).status_code == 200


def test_testimonials_only_published(api, seeded) -> None:
    Testimonial.objects.create(author_name="Awa", quote_fr="Super accueil", quote_en="Great")
    Testimonial.objects.create(author_name="Hidden", quote_fr="x", is_published=False)
    data = api.get("/api/v1/testimonials/", {"lang": "en"}).json()
    assert [t["author_name"] for t in data] == ["Awa"]
    assert data[0]["quote"] == "Great"


def test_team_only_active(api, seeded) -> None:
    TeamMember.objects.create(name="Paul", role_fr="Barber titulaire", role_en="Senior barber")
    TeamMember.objects.create(name="Gone", role_fr="Barber", is_active=False)
    data = api.get("/api/v1/team/").json()
    assert [m["name"] for m in data] == ["Paul"]
    assert data[0]["photo"] is None


def test_team_photo_is_exposed_as_responsive_image(api, seeded, make_image) -> None:
    TeamMember.objects.create(
        name="Paul", role_fr="Barber", photo=make_image(width=1200, height=1500)
    )
    photo = api.get("/api/v1/team/").json()[0]["photo"]
    assert photo["src"].startswith("http://testserver/media/team/")
    assert photo["srcset"].count("w, ") == 2  # 480w, 960w, 1200w
    assert photo["srcset"].endswith("1200w")
    assert (photo["width"], photo["height"]) == (1200, 1500)


def test_health_ok(api, db) -> None:
    response = api.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"database": "ok", "cache": "ok"}
    assert response["Cache-Control"] == "no-store"


def test_health_reports_database_failure(api, db, monkeypatch) -> None:
    def broken_cursor(*args, **kwargs):
        raise DatabaseError("down")

    monkeypatch.setattr("apps.core.views.connection.cursor", broken_cursor)
    response = api.get("/api/v1/health/")
    assert response.status_code == 503
    assert response.json()["database"] == "error"


def test_health_reports_degraded_cache(api, db, monkeypatch) -> None:
    monkeypatch.setattr("apps.core.views.cache.get", lambda *a, **k: None)
    assert api.get("/api/v1/health/").json()["cache"] == "degraded"
