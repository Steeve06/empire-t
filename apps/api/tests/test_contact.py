import logging

import pytest
from django.core import mail

from apps.contact.models import ContactMessage

pytestmark = pytest.mark.django_db

URL = "/api/v1/contact/"
VALID = {
    "name": "Awa Ngono",
    "contact": "awa@mail.cm",
    "message": "Faites-vous des tresses le dimanche ?",
}


def test_message_is_saved_and_shop_is_notified(
    api, seeded, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        response = api.post(URL, VALID, format="json")

    assert response.status_code == 201
    assert "Merci" in response.json()["detail"]
    message = ContactMessage.objects.get()
    assert (message.contact, message.contact_kind, message.status) == (
        "awa@mail.cm",
        "email",
        "new",
    )
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Nouveau message du site : Awa Ngono"
    assert "le dimanche" in mail.outbox[0].body


def test_english_response(api, seeded) -> None:
    response = api.post(f"{URL}?lang=en", {**VALID, "contact": "699001122"}, format="json")
    assert response.status_code == 201
    message = ContactMessage.objects.get()
    assert (message.contact, message.contact_kind, message.locale) == (
        "+237699001122",
        "phone",
        "en",
    )


def test_validation_errors_are_per_field(api, seeded) -> None:
    response = api.post(URL, {"name": "A", "contact": "nope", "message": "court"}, format="json")
    assert response.status_code == 400
    assert set(response.json()) == {"name", "contact", "message"}


def test_honeypot(api, seeded) -> None:
    assert api.post(URL, {**VALID, "website": "x"}, format="json").status_code == 400
    assert not ContactMessage.objects.exists()


def test_email_failure_never_loses_the_message(
    api, seeded, monkeypatch, caplog, django_capture_on_commit_callbacks
) -> None:
    def broken_send(*args, **kwargs):
        raise ConnectionError("SMTP down")

    monkeypatch.setattr("apps.core.notifications.send_mail", broken_send)
    with (
        caplog.at_level(logging.ERROR, logger="apps.core.notifications"),
        django_capture_on_commit_callbacks(execute=True),
    ):
        response = api.post(URL, VALID, format="json")

    assert response.status_code == 201
    assert ContactMessage.objects.count() == 1
    assert "Shop notification failed" in caplog.text


def test_contact_is_throttled(api, seeded, monkeypatch) -> None:
    from rest_framework.throttling import ScopedRateThrottle

    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "contact", "1/hour")
    assert api.post(URL, VALID, format="json").status_code == 201
    assert api.post(URL, VALID, format="json").status_code == 429
