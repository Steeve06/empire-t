"""Image pipeline: every uploaded photo is re-encoded as WebP at a few responsive widths.

The original upload is never kept. Variants are written next to each other as
``<upload_to>/<token>-<width>w.webp`` and their metadata is stored on the model so the API
can expose ``src``, ``srcset``, ``width`` and ``height`` without touching storage.
"""

from __future__ import annotations

import io
import logging
import secrets
from typing import TypedDict

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)

VARIANT_WIDTHS: tuple[int, ...] = (480, 960, 1600)
WEBP_QUALITY = 80
MAX_IMAGE_UPLOAD_BYTES = 12 * 1024 * 1024


class ImageVariant(TypedDict):
    width: int
    name: str


class ImageMeta(TypedDict):
    width: int
    height: int
    variants: list[ImageVariant]


def validate_image_upload_size(file: FieldFile) -> None:
    """Field validator: reject photos larger than 12 MB before processing them."""
    if file and file.size > MAX_IMAGE_UPLOAD_BYTES:
        raise ValidationError(_("L'image dépasse 12 Mo. Réduisez sa taille puis réessayez."))


def _target_widths(original_width: int) -> list[int]:
    widths = sorted({min(width, original_width) for width in VARIANT_WIDTHS})
    return widths or [original_width]


def _normalise_mode(image: Image.Image) -> Image.Image:
    has_alpha = image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info)
    return image.convert("RGBA" if has_alpha else "RGB")


def build_variants(file: FieldFile, upload_dir: str) -> ImageMeta:
    """Decode ``file``, write WebP variants to its storage and return their metadata."""
    storage: Storage = file.storage
    try:
        file.open("rb")
        with Image.open(file) as source:
            source.load()
            image = _normalise_mode(ImageOps.exif_transpose(source))
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError(_("Fichier image illisible ou corrompu.")) from exc

    token = secrets.token_hex(6)
    base = f"{upload_dir.rstrip('/')}/{token}"
    variants: list[ImageVariant] = []
    for width in _target_widths(image.width):
        height = round(image.height * width / image.width)
        resized = (
            image
            if width == image.width
            else image.resize((width, height), Image.Resampling.LANCZOS)
        )
        buffer = io.BytesIO()
        resized.save(buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
        saved_name = storage.save(f"{base}-{width}w.webp", ContentFile(buffer.getvalue()))
        variants.append({"width": width, "name": saved_name})

    largest = variants[-1]["width"]
    return {
        "width": largest,
        "height": round(image.height * largest / image.width),
        "variants": variants,
    }


def delete_variants(storage: Storage, meta: ImageMeta | None, keep: set[str] | None = None) -> None:
    """Remove stored variant files, ignoring the ones listed in ``keep``."""
    if not meta:
        return
    keep = keep or set()
    for variant in meta.get("variants", []):
        name = variant["name"]
        if name in keep:
            continue
        try:
            storage.delete(name)
        except OSError:
            logger.warning("Could not delete image variant %s", name, exc_info=True)
