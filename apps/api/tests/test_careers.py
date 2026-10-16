import datetime as dt
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.careers import uploads
from apps.careers.models import ApplicationFile, JobApplication, JobOpening
from apps.careers.uploads import sniff

pytestmark = pytest.mark.django_db

OPENINGS_URL = "/api/v1/careers/openings/"
APPLY_URL = "/api/v1/careers/applications/"

PDF = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\n"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
MP4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"


def pdf(name: str = "cv.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, PDF, content_type="application/pdf")


def jpeg(name: str = "realisation.jpg") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, JPEG, content_type="image/jpeg")


def application(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "opening": "barber-titulaire",
        "full_name": "Paul Essomba",
        "contact": "6 77 88 99 00",
        "message": "Barber depuis 4 ans à Bastos.",
        "files": [pdf(), jpeg()],
    }
    data.update(overrides)
    return data


def test_openings_list(api, seeded) -> None:
    data = api.get(OPENINGS_URL).json()
    assert [(o["slug"], o["positions_count"]) for o in data] == [
        ("barber-titulaire", 2),
        ("barber-remplacant", 3),
        ("estheticienne-titulaire", 1),
        ("estheticienne-remplacante", 3),
    ]
    assert data[0]["deadline"] == seeded.recruitment_deadline.isoformat()
    assert "2 ans" in data[0]["requirements"]


def test_openings_in_english(api, seeded) -> None:
    data = api.get(OPENINGS_URL, {"lang": "en"}).json()
    assert data[0]["title"] == "Permanent barber"


def test_openings_disappear_after_global_deadline(api, seeded) -> None:
    seeded.recruitment_deadline = timezone.localdate() - dt.timedelta(days=1)
    seeded.save()
    assert api.get(OPENINGS_URL).json() == []


def test_openings_hidden_without_deadline(api, seeded) -> None:
    seeded.recruitment_deadline = None
    seeded.save()
    assert api.get(OPENINGS_URL).json() == []


def test_opening_with_own_past_deadline_is_hidden(api, seeded) -> None:
    JobOpening.objects.filter(slug="barber-remplacant").update(
        deadline=timezone.localdate() - dt.timedelta(days=1)
    )
    slugs = [o["slug"] for o in api.get(OPENINGS_URL).json()]
    assert "barber-remplacant" not in slugs
    assert len(slugs) == 3


def test_effective_deadline_is_the_earliest(seeded) -> None:
    opening = JobOpening.objects.get(slug="barber-titulaire")
    opening.deadline = seeded.recruitment_deadline - dt.timedelta(days=5)
    assert opening.effective_deadline(seeded) == opening.deadline
    opening.deadline = None
    assert opening.effective_deadline(seeded) == seeded.recruitment_deadline


def test_application_is_stored_privately_and_notified(
    api, seeded, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        response = api.post(APPLY_URL, application(), format="multipart")

    assert response.status_code == 201, response.json()
    assert "Candidature envoyée" in response.json()["detail"]

    applicant = JobApplication.objects.get()
    assert applicant.contact == "+237677889900"
    assert applicant.contact_kind == "phone"
    assert applicant.opening.slug == "barber-titulaire"

    files = list(applicant.files.order_by("id"))
    assert [(f.original_name, f.kind, f.content_type) for f in files] == [
        ("cv.pdf", "pdf", "application/pdf"),
        ("realisation.jpg", "jpeg", "image/jpeg"),
    ]
    for stored in files:
        path = Path(stored.file.path)
        assert path.is_file()
        assert Path(settings.PRIVATE_MEDIA_ROOT) in path.parents
        assert Path(settings.MEDIA_ROOT) not in path.parents
        assert stored.original_name not in str(stored.file.name)  # random storage name

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == "Nouvelle candidature : Barber titulaire - Paul Essomba"
    assert email.to == [seeded.email]
    assert "cv.pdf" in email.body
    assert "/admin/careers/jobapplication/" in email.body


def test_notification_goes_to_notification_email_when_set(
    api, seeded, django_capture_on_commit_callbacks
) -> None:
    seeded.notification_email = "rh@empire-t.cm"
    seeded.save()
    with django_capture_on_commit_callbacks(execute=True):
        api.post(APPLY_URL, application(), format="multipart")
    assert mail.outbox[0].to == ["rh@empire-t.cm"]


def test_application_with_email_contact(api, seeded) -> None:
    api.post(APPLY_URL, application(contact="Paul@Mail.cm"), format="multipart")
    applicant = JobApplication.objects.get()
    assert (applicant.contact, applicant.contact_kind) == ("paul@mail.cm", "email")


def test_english_submission_still_notifies_in_french(
    api, seeded, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        response = api.post(
            f"{APPLY_URL}?lang=en",
            application(opening="estheticienne-titulaire"),
            format="multipart",
        )
    assert response.status_code == 201
    assert JobApplication.objects.get().locale == "en"
    # Email to the shop stays in French
    assert mail.outbox[0].subject.startswith("Nouvelle candidature : Esthéticienne titulaire")


@pytest.mark.parametrize(
    ("upload", "message_part"),
    [
        (SimpleUploadedFile("virus.exe", b"MZ\x90\x00"), "format non accepté"),
        (SimpleUploadedFile("cv.pdf", b"MZ\x90\x00\x03\x00\x00\x00"), "ne correspond pas"),
        (SimpleUploadedFile("photo.png", JPEG), "ne correspond pas"),
        (SimpleUploadedFile("page.pdf", b"<html><script>"), "ne correspond pas"),
    ],
)
def test_dangerous_or_spoofed_files_are_rejected(api, seeded, upload, message_part) -> None:
    response = api.post(APPLY_URL, application(files=[upload]), format="multipart")
    assert response.status_code == 400
    assert message_part in str(response.json()["files"])
    assert not JobApplication.objects.exists()


def test_empty_file_is_rejected(api, seeded) -> None:
    response = api.post(
        APPLY_URL, application(files=[SimpleUploadedFile("cv.pdf", b"")]), format="multipart"
    )
    assert response.status_code == 400


def test_application_without_files_is_rejected(api, seeded) -> None:
    data = application()
    del data["files"]
    response = api.post(APPLY_URL, data, format="multipart")
    assert response.status_code == 400
    assert "files" in response.json()


def test_too_many_files(api, seeded) -> None:
    files = [pdf(f"doc{i}.pdf") for i in range(uploads.MAX_FILES + 1)]
    response = api.post(APPLY_URL, application(files=files), format="multipart")
    assert response.status_code == 400


def test_file_size_limits(api, seeded, monkeypatch) -> None:
    monkeypatch.setattr(uploads, "MAX_FILE_BYTES", 10)
    response = api.post(APPLY_URL, application(), format="multipart")
    assert response.status_code == 400
    assert "15 Mo" in str(response.json()["files"])


def test_total_size_limit(api, seeded, monkeypatch) -> None:
    monkeypatch.setattr(uploads, "MAX_TOTAL_BYTES", len(PDF) + 1)
    response = api.post(APPLY_URL, application(), format="multipart")
    assert response.status_code == 400
    assert "40 Mo" in str(response.json()["files"])


def test_closed_recruitment_rejects_applications(api, seeded) -> None:
    seeded.recruitment_deadline = timezone.localdate() - dt.timedelta(days=1)
    seeded.save()
    response = api.post(APPLY_URL, application(), format="multipart")
    assert response.status_code == 400
    assert "opening" in response.json()
    assert not ApplicationFile.objects.exists()


def test_inactive_opening_is_rejected(api, seeded) -> None:
    JobOpening.objects.filter(slug="barber-titulaire").update(is_active=False)
    assert api.post(APPLY_URL, application(), format="multipart").status_code == 400


def test_invalid_contact(api, seeded) -> None:
    response = api.post(APPLY_URL, application(contact="pas un contact"), format="multipart")
    assert response.status_code == 400
    assert "contact" in response.json()


def test_honeypot(api, seeded) -> None:
    response = api.post(APPLY_URL, application(website="spam"), format="multipart")
    assert response.status_code == 400
    assert not JobApplication.objects.exists()


def test_json_body_is_not_accepted(api, seeded) -> None:
    response = api.post(APPLY_URL, {"opening": "barber-titulaire"}, format="json")
    assert response.status_code == 415


def test_deleting_an_application_deletes_its_files(api, seeded) -> None:
    api.post(APPLY_URL, application(), format="multipart")
    paths = [Path(f.file.path) for f in ApplicationFile.objects.all()]
    JobApplication.objects.get().delete()
    assert not any(p.exists() for p in paths)


@pytest.mark.parametrize(
    ("head", "kind"),
    [
        (PDF[:16], "pdf"),
        (b"PK\x03\x04\x14\x00\x06\x00", "docx"),
        (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00", "doc"),
        (JPEG[:16], "jpeg"),
        (b"\x89PNG\r\n\x1a\n\x00\x00", "png"),
        (b"RIFF\x24\x00\x00\x00WEBPVP8 ", "webp"),
        (MP4[:16], "mp4"),
        (b"\x00\x00\x00\x14ftypqt  \x00\x00", "mov"),
        (b"\x00\x00\x00\x18ftypheic\x00\x00", "heic"),
        (b"RIFF\x24\x00\x00\x00WAVEfmt ", None),
        (b"MZ\x90\x00", None),
    ],
)
def test_file_signatures(head: bytes, kind: str | None) -> None:
    assert sniff(head) == kind


def test_original_names_are_sanitised() -> None:
    assert uploads.safe_original_name("../../etc/Mon CV (final).PDF") == "Mon_CV_final.pdf"
    assert uploads.safe_original_name("???.pdf") == "document.pdf"
    assert uploads.safe_original_name("Résumé.pdf") == "Résumé.pdf"
