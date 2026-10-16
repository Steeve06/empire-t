import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.catalog.models import Service, ServiceCategory

pytestmark = pytest.mark.django_db


def test_categories_menu_matches_the_price_list(api, seeded) -> None:
    data = api.get("/api/v1/categories/").json()

    assert [c["slug"] for c in data] == ["men", "women", "kids", "beauty", "packs"]
    assert {c["slug"]: len(c["services"]) for c in data} == {
        "men": 9,
        "women": 5,
        "kids": 2,
        "beauty": 4,
        "packs": 3,
    }
    assert {c["slug"]: c["starting_price"] for c in data} == {
        "men": 500,
        "women": 3000,
        "kids": 1000,
        "beauty": 2000,
        "packs": 1000,
    }
    beauty = next(c for c in data if c["slug"] == "beauty")
    assert beauty["accent"] == "rose"
    women = next(c for c in data if c["slug"] == "women")
    assert women["appointment_only"] is True
    assert women["booking_note"] == "Sur rendez-vous"
    packs = next(c for c in data if c["slug"] == "packs")
    assert packs["show_on_home"] is False


def test_service_rows_carry_price_flags(api, seeded) -> None:
    data = api.get("/api/v1/categories/women/").json()
    by_slug = {s["slug"]: s for s in data["services"]}
    assert by_slug["twists-vanilles"]["price"] == 3000
    assert by_slug["twists-vanilles"]["price_is_from"] is True
    assert (
        by_slug["twists-vanilles"]["duration_min"],
        by_slug["twists-vanilles"]["duration_max"],
    ) == (60, 90)
    assert by_slug["locks-complexes"]["price"] is None
    assert by_slug["locks-complexes"]["price_on_quote"] is True
    assert "category" not in by_slug["retwist"]


def test_categories_in_english(api, seeded) -> None:
    men = api.get("/api/v1/categories/men/", {"lang": "en"}).json()
    assert men["name"] == "Men"
    assert men["title"] == "Men's Barbershop"
    assert men["services"][0]["name"] == "Classic haircut"


def test_inactive_services_and_categories_are_hidden(api, seeded) -> None:
    Service.objects.filter(slug="skin-fade").update(is_active=False)
    ServiceCategory.objects.filter(slug="kids").update(is_active=False)

    data = api.get("/api/v1/categories/").json()
    assert "kids" not in [c["slug"] for c in data]
    men = next(c for c in data if c["slug"] == "men")
    assert "skin-fade" not in [s["slug"] for s in men["services"]]
    assert api.get("/api/v1/services/coupe-enfant/").status_code == 404


def test_unknown_category_is_404(api, seeded) -> None:
    assert api.get("/api/v1/categories/nope/").status_code == 404


def test_services_list_is_paginated_and_filterable(api, seeded) -> None:
    data = api.get("/api/v1/services/").json()
    assert data["count"] == 23
    assert len(data["results"]) == 23

    men = api.get("/api/v1/services/", {"category": "men", "page_size": 5}).json()
    assert men["count"] == 9
    assert len(men["results"]) == 5
    assert men["next"] is not None
    assert {s["category"] for s in men["results"]} == {"men"}


def test_popular_services(api, seeded) -> None:
    data = api.get("/api/v1/services/", {"popular": "true"}).json()
    assert [s["slug"] for s in data["results"]] == [
        "coupe-simple",
        "fade",
        "nattes-cornrows",
        "coupe-barbe",
    ]


def test_service_detail(api, seeded) -> None:
    data = api.get("/api/v1/services/empire-premium/").json()
    assert data["category"] == "packs"
    assert data["price"] == 3500
    assert (data["duration_min"], data["duration_max"]) == (50, 60)


def test_supplements(api, seeded) -> None:
    data = api.get("/api/v1/supplements/", {"lang": "en"}).json()
    assert [(s["name"], s["price"], s["price_is_from"]) for s in data] == [
        ("Scalp massage", 1000, False),
        ("Hot towel", 500, False),
        ("Full shave", 1500, False),
        ("Colouring", 3000, True),
    ]


def test_category_list_query_count_does_not_grow(
    api, seeded, django_assert_max_num_queries
) -> None:
    men = ServiceCategory.objects.get(slug="men")
    for i in range(15):
        Service.objects.create(
            category=men, slug=f"extra-{i}", name_fr=f"Extra {i}", duration_min=20, price=1000
        )
    # categories + prefetched services; never one query per category or per service
    with django_assert_max_num_queries(2):
        assert api.get("/api/v1/categories/").status_code == 200


def test_service_list_query_count(api, seeded, django_assert_max_num_queries) -> None:
    with django_assert_max_num_queries(2):  # count + page, category joined
        assert api.get("/api/v1/services/").status_code == 200


def test_price_constraint_rejects_missing_price(seeded) -> None:
    men = ServiceCategory.objects.get(slug="men")
    with pytest.raises(IntegrityError), transaction.atomic():
        Service.objects.create(category=men, slug="bad", name_fr="Bad", duration_min=20)


def test_price_constraint_rejects_price_with_quote(seeded) -> None:
    men = ServiceCategory.objects.get(slug="men")
    with pytest.raises(IntegrityError), transaction.atomic():
        Service.objects.create(
            category=men, slug="bad", name_fr="Bad", duration_min=20, price=10, price_on_quote=True
        )


def test_duration_constraint(seeded) -> None:
    men = ServiceCategory.objects.get(slug="men")
    with pytest.raises(IntegrityError), transaction.atomic():
        Service.objects.create(
            category=men, slug="bad", name_fr="Bad", duration_min=40, duration_max=20, price=10
        )


def test_clean_gives_friendly_admin_errors(seeded) -> None:
    men = ServiceCategory.objects.get(slug="men")
    service = Service(category=men, slug="x", name_fr="X", duration_min=40, duration_max=20)
    with pytest.raises(ValidationError) as error:
        service.clean()
    assert set(error.value.message_dict) == {"price", "duration_max"}

    quote = Service(
        category=men, slug="y", name_fr="Y", duration_min=40, price=5, price_on_quote=True
    )
    with pytest.raises(ValidationError):
        quote.clean()


def test_longest_duration(seeded) -> None:
    assert Service.objects.get(slug="skin-fade").longest_duration == 40
    assert Service.objects.get(slug="coupe-simple").longest_duration == 20
