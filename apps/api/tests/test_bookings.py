import datetime as dt
import re

import pytest
from django.utils import timezone
from rest_framework.throttling import ScopedRateThrottle

from apps.bookings.models import BookingChannel, BookingRequest, BookingStatus, PaymentStatus
from apps.bookings.services import available_slots, booking_message, customer_whatsapp_url
from apps.catalog.models import Service

from .helpers import future_date, whatsapp_text

pytestmark = pytest.mark.django_db

URL = "/api/v1/bookings/"


def payload(**overrides: str) -> dict[str, str]:
    data = {
        "service": "empire-premium",
        "date": future_date().isoformat(),
        "time_slot": "14:30",
        "customer_name": "Jean Mballa",
        "phone": "6 53 14 75 12",
    }
    data.update(overrides)
    return data


def at_douala(day: dt.date, hour: int, minute: int = 0) -> dt.datetime:
    return timezone.make_aware(dt.datetime.combine(day, dt.time(hour, minute)))


def test_booking_is_stored_and_returns_whatsapp_link(api, seeded) -> None:
    response = api.post(URL, payload(notes="Première visite"), format="json")

    assert response.status_code == 201
    data = response.json()
    assert re.fullmatch(r"ET-[A-HJKMNP-Z2-9]{6}", data["reference"])
    assert data["status"] == "new"
    assert data["service"] == "empire-premium"
    assert data["time_slot"] == "14:30"

    booking = BookingRequest.objects.get(reference=data["reference"])
    assert booking.phone == "+237653147512"
    assert booking.service_name == "Empire Premium"
    assert booking.price_snapshot == 3500
    assert booking.duration_minutes == 60
    assert booking.locale == "fr"
    assert booking.channel == BookingChannel.WEBSITE
    assert booking.payment_status == PaymentStatus.NOT_REQUIRED
    assert booking.ends_at - booking.starts_at == dt.timedelta(minutes=60)

    assert data["whatsapp_url"].startswith("https://wa.me/237653147512?text=")
    text = whatsapp_text(data["whatsapp_url"])
    assert "Je souhaite réserver" in text
    assert "Prestation : Empire Premium" in text
    assert "Heure : 14h30" in text
    assert "Nom : Jean Mballa" in text
    assert "Téléphone : 653 147 512" in text
    assert "Note : Première visite" in text
    assert data["reference"] in text


def test_dates_are_spelled_out_in_each_language(seeded) -> None:
    day = dt.date(2026, 12, 19)  # a Saturday
    booking = BookingRequest(
        reference="ET-AAAAAA",
        service=Service.objects.get(slug="fade"),
        service_name="Low, Mid, High Fade",
        duration_minutes=30,
        date=day,
        time_slot=dt.time(9, 0),
        customer_name="Awa",
        phone="+237699001122",
    )
    assert "Date : samedi 19 décembre 2026" in booking_message(booking)
    booking.locale = "en"
    message = booking_message(booking)
    assert "Date: Saturday 19 December 2026" in message
    assert "Time: 09:00" in message


def test_english_booking_message(api, seeded) -> None:
    data = api.post(f"{URL}?lang=en", payload(), format="json").json()
    text = whatsapp_text(data["whatsapp_url"])
    assert text.startswith("Hello Empire T! I would like to book:")
    assert "Time: 14:30" in text
    assert BookingRequest.objects.get().service_name == "Empire Premium"


def test_quick_bar_channel_is_recorded(api, seeded) -> None:
    api.post(URL, payload(channel="quick_bar"), format="json")
    assert BookingRequest.objects.get().channel == BookingChannel.QUICK_BAR


def test_admin_channel_cannot_be_forged(api, seeded) -> None:
    response = api.post(URL, payload(channel="admin"), format="json")
    assert response.status_code == 400
    assert "channel" in response.json()


def test_name_is_collapsed_to_one_line(api, seeded) -> None:
    api.post(URL, payload(customer_name="  Jean \n\n Mballa "), format="json")
    assert BookingRequest.objects.get().customer_name == "Jean Mballa"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("phone", "12345"),
        ("customer_name", "J"),
        ("service", "does-not-exist"),
        ("time_slot", "25:00"),
        ("date", "not-a-date"),
    ],
)
def test_invalid_fields_are_rejected(api, seeded, field, value) -> None:
    response = api.post(URL, payload(**{field: value}), format="json")
    assert response.status_code == 400
    assert field in response.json()
    assert not BookingRequest.objects.exists()


def test_past_date_is_rejected(api, seeded) -> None:
    yesterday = timezone.localdate() - dt.timedelta(days=1)
    response = api.post(URL, payload(date=yesterday.isoformat()), format="json")
    assert response.status_code == 400
    assert "date" in response.json()


def test_date_beyond_horizon_is_rejected(api, seeded) -> None:
    response = api.post(URL, payload(date=future_date(61).isoformat()), format="json")
    assert response.status_code == 400
    assert "date" in response.json()


@pytest.mark.parametrize("slot", ["06:30", "21:00", "14:10", "20:30"])
def test_slot_outside_offered_times_is_rejected(api, seeded, slot) -> None:
    # 20:30 + 50 min for Empire Premium would end after closing time
    response = api.post(URL, payload(time_slot=slot), format="json")
    assert response.status_code == 400
    assert "time_slot" in response.json()


def test_slot_too_soon_today_is_rejected(api, seeded, monkeypatch) -> None:
    today = timezone.localdate()
    monkeypatch.setattr("apps.bookings.services.timezone.now", lambda: at_douala(today, 10, 5))
    monkeypatch.setattr("apps.bookings.serializers.timezone.localdate", lambda: today)

    too_soon = api.post(URL, payload(date=today.isoformat(), time_slot="10:30"), format="json")
    assert too_soon.status_code == 400

    ok = api.post(URL, payload(date=today.isoformat(), time_slot="11:00"), format="json")
    assert ok.status_code == 201


def test_inactive_service_cannot_be_booked(api, seeded) -> None:
    Service.objects.filter(slug="empire-premium").update(is_active=False)
    response = api.post(URL, payload(), format="json")
    assert response.status_code == 400
    assert "service" in response.json()


def test_quote_only_service_can_be_requested(api, seeded) -> None:
    response = api.post(URL, payload(service="locks-complexes", time_slot="09:00"), format="json")
    assert response.status_code == 201
    assert BookingRequest.objects.get().price_snapshot is None


def test_honeypot_blocks_bots(api, seeded) -> None:
    response = api.post(URL, payload(website="http://spam.example"), format="json")
    assert response.status_code == 400
    assert not BookingRequest.objects.exists()


def test_bookings_are_throttled(api, seeded, monkeypatch) -> None:
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "bookings", "2/hour")
    statuses = [api.post(URL, payload(), format="json").status_code for _ in range(3)]
    assert statuses == [201, 201, 429]


def test_booking_without_site_settings_is_404(api, db) -> None:
    assert api.post(URL, payload(), format="json").status_code == 404


def test_slots_endpoint(api, seeded) -> None:
    day = future_date()
    data = api.get(f"{URL}slots/", {"date": day.isoformat(), "service": "skin-fade"}).json()
    assert data["date"] == day.isoformat()
    assert data["slots"][0] == "07:00"
    assert data["slots"][-1] == "20:00"  # 20:00 + 35 min fits before 21:00, 20:30 does not
    assert len(data["slots"]) == 27


def test_slots_endpoint_without_service_uses_slot_interval(api, seeded) -> None:
    data = api.get(f"{URL}slots/", {"date": future_date().isoformat()}).json()
    assert data["slots"][-1] == "20:30"


def test_slots_endpoint_validates_query(api, seeded) -> None:
    assert api.get(f"{URL}slots/").status_code == 400
    assert api.get(f"{URL}slots/", {"date": "2026-02-30"}).status_code == 400


def test_no_slots_outside_horizon(seeded) -> None:
    assert available_slots(seeded, timezone.localdate() - dt.timedelta(days=1)) == []
    assert available_slots(seeded, future_date(seeded.booking_horizon_days + 1)) == []


def test_late_evening_today_has_no_slots(seeded) -> None:
    today = timezone.localdate()
    assert available_slots(seeded, today, now=at_douala(today, 20, 45)) == []


def test_customer_confirmation_link(seeded) -> None:
    booking = BookingRequest.objects.create(
        service=Service.objects.get(slug="fade"),
        service_name="Low, Mid, High Fade",
        duration_minutes=30,
        date=future_date(),
        time_slot=dt.time(9, 30),
        customer_name="Awa",
        phone="+237699001122",
    )
    url = customer_whatsapp_url(booking)
    assert url.startswith("https://wa.me/237699001122?text=")
    assert "est confirmée" in whatsapp_text(url)
    booking.locale = "en"
    assert "is confirmed" in whatsapp_text(customer_whatsapp_url(booking))
    assert str(booking).startswith(booking.reference)
    assert booking.status == BookingStatus.NEW
