from pathlib import Path

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.core.images import MAX_IMAGE_UPLOAD_BYTES, validate_image_upload_size
from apps.gallery.models import GalleryCategory, GalleryImage

pytestmark = pytest.mark.django_db


def stored(name: str) -> Path:
    return Path(settings.MEDIA_ROOT) / name


def create_gallery_image(upload: SimpleUploadedFile) -> GalleryImage:
    return GalleryImage.objects.create(
        category=GalleryCategory.CUTS, image=upload, alt_text_fr="Dégradé", alt_text_en="Fade"
    )


def test_large_photo_becomes_three_webp_variants(make_image) -> None:
    image = create_gallery_image(make_image(width=2400, height=1600))

    meta = image.image_meta["image"]
    assert [v["width"] for v in meta["variants"]] == [480, 960, 1600]
    assert (meta["width"], meta["height"]) == (1600, 1067)
    assert image.image.name == meta["variants"][-1]["name"]
    for variant in meta["variants"]:
        assert variant["name"].endswith(f"-{variant['width']}w.webp")
        with Image.open(stored(variant["name"])) as webp:
            assert webp.format == "WEBP"
            assert webp.width == variant["width"]


def test_small_photo_is_never_upscaled(make_image) -> None:
    image = create_gallery_image(make_image(width=300, height=200))
    assert [v["width"] for v in image.image_meta["image"]["variants"]] == [300]


def test_transparent_png_keeps_alpha(make_image) -> None:
    image = create_gallery_image(
        make_image(width=600, height=600, fmt="PNG", mode="RGBA", name="logo.png")
    )
    with Image.open(stored(str(image.image.name))) as webp:
        assert webp.mode == "RGBA"


def test_replacing_a_photo_deletes_old_variants(make_image) -> None:
    image = create_gallery_image(make_image())
    old_names = [v["name"] for v in image.image_meta["image"]["variants"]]

    image.image = make_image(width=1000, height=1000)
    image.save()

    assert all(not stored(name).exists() for name in old_names)
    assert all(stored(v["name"]).exists() for v in image.image_meta["image"]["variants"])


def test_saving_without_new_upload_does_not_reprocess(make_image) -> None:
    image = create_gallery_image(make_image())
    names = [v["name"] for v in image.image_meta["image"]["variants"]]
    image.order = 5
    image.save(update_fields=["order"])
    image.refresh_from_db()
    assert [v["name"] for v in image.image_meta["image"]["variants"]] == names


def test_update_fields_save_persists_new_image(make_image) -> None:
    image = create_gallery_image(make_image())
    image.image = make_image(width=800, height=800)
    image.save(update_fields=["image"])
    image.refresh_from_db()
    assert image.image_meta["image"]["width"] == 800


def test_clearing_an_image_removes_files_and_metadata(make_image, seeded) -> None:
    seeded.hero_image = make_image()
    seeded.save()
    names = [v["name"] for v in seeded.image_meta["hero_image"]["variants"]]

    seeded.hero_image = None
    seeded.save()

    assert "hero_image" not in seeded.image_meta
    assert all(not stored(name).exists() for name in names)


def test_deleting_the_row_deletes_the_files(make_image) -> None:
    image = create_gallery_image(make_image())
    names = [v["name"] for v in image.image_meta["image"]["variants"]]
    image.delete()
    assert all(not stored(name).exists() for name in names)


def test_corrupt_upload_is_rejected() -> None:
    with pytest.raises(ValidationError):
        create_gallery_image(SimpleUploadedFile("x.jpg", b"definitely not an image"))


def test_upload_size_validator() -> None:
    class FakeFile:
        size = MAX_IMAGE_UPLOAD_BYTES + 1

        def __bool__(self) -> bool:
            return True

    with pytest.raises(ValidationError):
        validate_image_upload_size(FakeFile())  # type: ignore[arg-type]
