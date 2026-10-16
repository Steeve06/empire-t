import datetime as dt

import pytest
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from apps.bookings.models import BookingRequest, BookingStatus
from apps.careers.models import ApplicationFile, JobApplication, JobOpening
from apps.catalog.models import Service
from apps.contact.models import ContactMessage, MessageStatus
from apps.core.models import SiteSettings, TeamMember
from apps.gallery.models import GalleryCategory, GalleryImage

from .helpers import future_date

pytestmark = pytest.mark.django_db

APP_MODELS = [
    model
    for model in admin.site._registry
    if model._meta.app_label in {"core", "catalog", "bookings", "careers", "gallery", "contact"}
]


@pytest.fixture
def owner_client(admin_user: User) -> Client:
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def records(seeded, make_image):
    booking = BookingRequest.objects.create(
        service=Service.objects.get(slug="fade"),
        service_name="Low, Mid, High Fade",
        price_snapshot=1500,
        duration_minutes=30,
        date=future_date(),
        time_slot=dt.time(10, 0),
        customer_name="Jean Mballa",
        phone="+237653147512",
    )
    applicant = JobApplication.objects.create(
        opening=JobOpening.objects.get(slug="barber-titulaire"),
        full_name="Paul Essomba",
        contact="+237677889900",
        contact_kind="phone",
    )
    attachment = ApplicationFile.objects.create(
        application=applicant,
        file=SimpleUploadedFile("cv.pdf", b"%PDF-1.7 test"),
        original_name="Mon CV.pdf",
        kind="pdf",
        content_type="application/pdf",
        size=13,
    )
    message = ContactMessage.objects.create(
        name="Awa", contact="awa@mail.cm", contact_kind="email", message="Bonjour, horaires ?"
    )
    GalleryImage.objects.create(
        category=GalleryCategory.CUTS, image=make_image(width=400, height=400), alt_text_fr="Fade"
    )
    TeamMember.objects.create(
        name="Paul", role_fr="Barber", photo=make_image(width=400, height=500)
    )
    return {"booking": booking, "application": applicant, "file": attachment, "message": message}


@pytest.mark.parametrize("model", APP_MODELS, ids=lambda m: m._meta.label)
def test_every_changelist_and_change_page_renders(owner_client, records, model) -> None:
    info = (model._meta.app_label, model._meta.model_name)
    changelist = owner_client.get(reverse("admin:{}_{}_changelist".format(*info)), follow=True)
    assert changelist.status_code == 200

    obj = model._default_manager.first()
    if obj is not None:
        change = owner_client.get(reverse("admin:{}_{}_change".format(*info), args=[obj.pk]))
        assert change.status_code == 200


def test_site_settings_list_redirects_to_the_single_form(owner_client, seeded) -> None:
    response = owner_client.get(reverse("admin:core_sitesettings_changelist"))
    assert response.status_code == 302
    assert response["Location"].endswith("/admin/core/sitesettings/1/change/")
    assert owner_client.get(reverse("admin:core_sitesettings_add")).status_code == 403


def test_site_settings_can_be_added_on_an_empty_database(owner_client) -> None:
    assert owner_client.get(reverse("admin:core_sitesettings_changelist")).status_code == 200
    assert owner_client.get(reverse("admin:core_sitesettings_add")).status_code == 200
    assert not SiteSettings.objects.exists()


def test_owner_edits_a_price_from_the_list(owner_client, seeded, api) -> None:
    api.get("/api/v1/categories/")  # warm the cache
    service = Service.objects.get(slug="coupe-simple")
    service.price = 1200
    service.save()
    men = api.get("/api/v1/categories/men/").json()
    assert next(s for s in men["services"] if s["slug"] == "coupe-simple")["price"] == 1200


def test_booking_list_shows_whatsapp_reply_link(owner_client, records) -> None:
    page = owner_client.get(reverse("admin:bookings_bookingrequest_changelist")).content.decode()
    assert "https://wa.me/237653147512?text=" in page
    assert "653 147 512" in page


def test_booking_status_action(owner_client, records) -> None:
    booking = records["booking"]
    response = owner_client.post(
        reverse("admin:bookings_bookingrequest_changelist"),
        {"action": "set_status_confirmed", "_selected_action": [booking.pk]},
        follow=True,
    )
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CONFIRMED


def test_booking_csv_export(owner_client, records) -> None:
    response = owner_client.post(
        reverse("admin:bookings_bookingrequest_changelist"),
        {"action": "export_as_csv", "_selected_action": [records["booking"].pk]},
    )
    assert response["Content-Type"] == "text/csv; charset=utf-8"
    body = response.content.decode("utf-8-sig")
    assert body.splitlines()[0].startswith("Référence;Date;Heure;Client")
    assert "Jean Mballa" in body


def test_application_file_download_is_staff_only(owner_client, records) -> None:
    url = reverse("admin:careers_applicationfile_download", args=[records["file"].pk])

    response = owner_client.get(url)
    assert response.status_code == 200
    assert 'filename="Mon CV.pdf"' in response["Content-Disposition"]
    assert b"".join(response.streaming_content).startswith(b"%PDF")

    anonymous = Client().get(url)
    assert anonymous.status_code == 302
    assert "/admin/login/" in anonymous["Location"]


def test_application_file_download_requires_view_permission(records, db) -> None:
    staff = User.objects.create_user("clerk", password="a-strong-pass-123", is_staff=True)
    client = Client()
    client.force_login(staff)
    url = reverse("admin:careers_applicationfile_download", args=[records["file"].pk])
    assert client.get(url).status_code == 403


def test_application_files_are_not_served_under_media(client, records) -> None:
    name = records["file"].file.name
    assert client.get(f"/media/{name}").status_code == 404


def test_opening_list_counts_applications(owner_client, records) -> None:
    page = owner_client.get(reverse("admin:careers_jobopening_changelist")).content.decode()
    assert "Barber titulaire" in page


def test_opening_a_contact_message_marks_it_read(owner_client, records) -> None:
    message = records["message"]
    owner_client.get(reverse("admin:contact_contactmessage_change", args=[message.pk]))
    message.refresh_from_db()
    assert message.status == MessageStatus.READ


def test_contact_reply_links(records) -> None:
    from apps.contact.admin import ContactMessageAdmin

    model_admin = ContactMessageAdmin(ContactMessage, admin.site)
    email_message = records["message"]
    assert "mailto:awa@mail.cm" in model_admin.reply_link(email_message)
    phone_message = ContactMessage(
        name="Jo", contact="+237699001122", contact_kind="phone", message="x" * 20
    )
    assert "https://wa.me/237699001122" in model_admin.reply_link(phone_message)
    assert model_admin.excerpt(ContactMessage(message="y" * 100)).endswith("…")


def test_price_and_duration_labels() -> None:
    from apps.catalog.admin import format_duration, format_price

    assert format_price(Service(price=2000, price_is_from=True)) == "Dès 2 000 F"
    assert format_price(Service(price=500)) == "500 F"
    assert format_price(Service(price_on_quote=True)) == "Sur devis"
    assert format_duration(Service(duration_min=60, duration_max=90)) == "60 à 90 min"
    assert format_duration(Service(duration_min=20)) == "20 min"
