"""Validation of job application attachments.

Checks the extension *and* the file's leading bytes, so a renamed executable or HTML file is
rejected even with a ``.pdf`` name. Limits are sized for photos and short videos sent from a
phone on a mobile connection.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import PurePath

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import get_valid_filename
from django.utils.translation import gettext as _

MAX_FILES = 8
MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_TOTAL_BYTES = 40 * 1024 * 1024


@dataclass(frozen=True)
class FileKind:
    code: str
    content_type: str
    extensions: tuple[str, ...]


KINDS: dict[str, FileKind] = {
    "pdf": FileKind("pdf", "application/pdf", (".pdf",)),
    "docx": FileKind(
        "docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        (".docx",),
    ),
    "doc": FileKind("doc", "application/msword", (".doc",)),
    "jpeg": FileKind("jpeg", "image/jpeg", (".jpg", ".jpeg")),
    "png": FileKind("png", "image/png", (".png",)),
    "webp": FileKind("webp", "image/webp", (".webp",)),
    "heic": FileKind("heic", "image/heic", (".heic", ".heif")),
    "mp4": FileKind("mp4", "video/mp4", (".mp4", ".m4v")),
    "mov": FileKind("mov", "video/quicktime", (".mov",)),
}

ALLOWED_EXTENSIONS = sorted({ext for kind in KINDS.values() for ext in kind.extensions})
_HEIC_BRANDS = {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}


class UploadRejected(ValueError):
    """Raised with a user-facing (translated) message."""


# kind -> byte patterns that must all match at their offsets. ISO media ("ftyp") is handled
# separately because the brand decides between HEIC, MOV and MP4.
_SIGNATURES: dict[str, tuple[tuple[int, bytes], ...]] = {
    "pdf": ((0, b"%PDF-"),),
    "docx": ((0, b"PK\x03\x04"),),
    "doc": ((0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),),
    "jpeg": ((0, b"\xff\xd8\xff"),),
    "png": ((0, b"\x89PNG\r\n\x1a\n"),),
    "webp": ((0, b"RIFF"), (8, b"WEBP")),
}


def sniff(head: bytes) -> str | None:
    """Identify the file type from its first 16 bytes."""
    for kind, parts in _SIGNATURES.items():
        if all(head[offset : offset + len(magic)] == magic for offset, magic in parts):
            return kind
    if head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand in _HEIC_BRANDS:
            return "heic"
        return "mov" if brand == b"qt  " else "mp4"
    return None


def safe_original_name(name: str) -> str:
    path = PurePath(name)
    try:
        stem = get_valid_filename(path.stem)[:80]
    except SuspiciousFileOperation:  # nothing usable left, e.g. "???" or only emoji
        stem = "document"
    return f"{stem}{path.suffix.lower()}"


def validate_upload(upload: UploadedFile[bytes]) -> FileKind:
    name = upload.name or ""
    extension = PurePath(name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise UploadRejected(
            _("« %(name)s » : format non accepté. Formats acceptés : PDF, Word, photos, vidéos.")
            % {"name": name}
        )
    if upload.size is None or upload.size == 0:
        raise UploadRejected(_("« %(name)s » est vide.") % {"name": name})
    if upload.size > MAX_FILE_BYTES:
        raise UploadRejected(_("« %(name)s » dépasse 15 Mo.") % {"name": name})

    upload.seek(0)
    head = upload.read(16)
    upload.seek(0)
    detected = sniff(head)
    kind = KINDS.get(detected or "")
    if kind is None or extension not in kind.extensions:
        raise UploadRejected(
            _("« %(name)s » ne correspond pas à son extension ou est endommagé.") % {"name": name}
        )
    return kind


def validate_upload_set(uploads: Sequence[UploadedFile[bytes]]) -> list[FileKind]:
    if not uploads:
        raise UploadRejected(_("Ajoutez au moins votre CV."))
    if len(uploads) > MAX_FILES:
        raise UploadRejected(_("%(max)d fichiers maximum.") % {"max": MAX_FILES})
    if sum(upload.size or 0 for upload in uploads) > MAX_TOTAL_BYTES:
        raise UploadRejected(_("L'ensemble des fichiers dépasse 40 Mo."))
    return [validate_upload(upload) for upload in uploads]
