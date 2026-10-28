"""Visitors get API messages in the language of the page they are on."""

import datetime as dt

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db

BOOKING = {
    "service": "coupe-simple",
    "time_slot": "10:00",
    "customer_name": "Ana",
    "phone": "123",
}


@pytest.mark.parametrize(
    ("lang", "date_error", "phone_error"),
    [
        ("fr", "Choisissez une date à venir.", "Numéro invalide."),
        ("en", "Choose a future date.", "Invalid number."),
    ],
)
def test_booking_validation_errors_follow_the_language(
    api, seeded, lang, date_error, phone_error
) -> None:
    yesterday = (timezone.localdate() - dt.timedelta(days=1)).isoformat()
    response = api.post(
        f"/api/v1/bookings/?lang={lang}", {**BOOKING, "date": yesterday}, format="json"
    )
    assert response.status_code == 400
    body = response.json()
    assert body["date"] == [date_error]
    assert body["phone"][0].startswith(phone_error)


def test_contact_confirmation_in_english(api, seeded) -> None:
    response = api.post(
        "/api/v1/contact/?lang=en",
        {"name": "Ana", "contact": "ana@mail.cm", "message": "Do you braid on Sundays?"},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["detail"].startswith("Thank you!")


def test_unknown_api_path_in_english(api, db) -> None:
    response = api.get("/api/v1/nope/?lang=en")
    assert response.status_code == 404
    assert response.json() == {"detail": "Resource not found."}
