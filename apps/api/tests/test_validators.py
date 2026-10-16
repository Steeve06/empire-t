import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import format_cameroon_display, normalize_contact, normalize_phone
from apps.core.whatsapp import whatsapp_link


@pytest.mark.parametrize(
    "raw",
    [
        "653147512",
        "6 53 14 75 12",
        "653-147-512",
        "+237 653 147 512",
        "237653147512",
        "00237653147512",
    ],
)
def test_cameroon_mobile_numbers_are_normalised(raw: str) -> None:
    assert normalize_phone(raw) == "+237653147512"


def test_cameroon_landline_is_accepted() -> None:
    assert normalize_phone("222 23 45 67") == "+237222234567"


def test_foreign_number_in_international_format_is_accepted() -> None:
    assert normalize_phone("+33 6 12 34 56 78") == "+33612345678"


@pytest.mark.parametrize("raw", ["", "12345", "753147512", "6531475120", "abc", "+0123456789"])
def test_invalid_numbers_are_rejected(raw: str) -> None:
    with pytest.raises(ValidationError):
        normalize_phone(raw)


def test_contact_accepts_email_and_lowercases_it() -> None:
    assert normalize_contact("  Awa.Ngono@Mail.CM ") == ("awa.ngono@mail.cm", "email")


def test_contact_accepts_phone() -> None:
    assert normalize_contact("6 99 00 11 22") == ("+237699001122", "phone")


@pytest.mark.parametrize("raw", ["not-an-email@", "@x", "hello", ""])
def test_contact_rejects_garbage(raw: str) -> None:
    with pytest.raises(ValidationError):
        normalize_contact(raw)


def test_display_format() -> None:
    assert format_cameroon_display("+237653147512") == "653 147 512"
    assert format_cameroon_display("+33612345678") == "+33612345678"


def test_whatsapp_link_encodes_everything() -> None:
    url = whatsapp_link("+237653147512", "Bonjour & à bientôt ?\nRéf : 1")
    assert url.startswith("https://wa.me/237653147512?text=")
    assert "&" not in url.split("?text=")[1]
    assert "%0A" in url
