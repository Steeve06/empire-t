from urllib.parse import quote


def whatsapp_link(phone_e164: str, message: str) -> str:
    """Build a click-to-chat link (https://wa.me/<digits>?text=...) with a prefilled message."""
    digits = phone_e164.lstrip("+")
    return f"https://wa.me/{digits}?text={quote(message, safe='')}"
