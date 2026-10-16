import pytest

from apps.catalog.models import Service
from apps.gallery.models import GalleryCategory, GalleryImage

pytestmark = pytest.mark.django_db

URL = "/api/v1/gallery/"


@pytest.fixture
def gallery(seeded, make_image):
    fade = Service.objects.get(slug="fade")
    images = [
        GalleryImage.objects.create(
            category=GalleryCategory.CUTS,
            image=make_image(width=900, height=1200),
            alt_text_fr="Dégradé bas avec contours nets",
            alt_text_en="Low fade with sharp line up",
            service=fade,
            is_featured=True,
            order=1,
        ),
        GalleryImage.objects.create(
            category=GalleryCategory.BEAUTY,
            image=make_image(width=900, height=900),
            alt_text_fr="Manucure nude",
            order=2,
        ),
        GalleryImage.objects.create(
            category=GalleryCategory.SALON,
            image=make_image(width=900, height=600),
            alt_text_fr="Espace d'attente",
            is_published=False,
            order=3,
        ),
    ]
    return images


def test_lists_published_images_in_order(api, gallery) -> None:
    data = api.get(URL).json()
    assert data["count"] == 2
    first = data["results"][0]
    assert first["category"] == "cuts"
    assert first["service"] == "fade"
    assert first["alt_text"] == "Dégradé bas avec contours nets"
    assert first["image"]["width"] == 900
    assert first["image"]["srcset"].endswith("900w")
    assert data["results"][1]["service"] is None


def test_filters(api, gallery) -> None:
    assert api.get(URL, {"category": "beauty"}).json()["count"] == 1
    assert api.get(URL, {"featured": "true"}).json()["count"] == 1
    assert api.get(URL, {"category": "salon"}).json()["count"] == 0
    assert api.get(URL, {"category": "nope"}).status_code == 400


def test_english_alt_text_with_french_fallback(api, gallery) -> None:
    results = api.get(URL, {"lang": "en"}).json()["results"]
    assert results[0]["alt_text"] == "Low fade with sharp line up"
    assert results[1]["alt_text"] == "Manucure nude"  # no English yet -> French


def test_cache_invalidated_when_a_photo_is_unpublished(api, gallery) -> None:
    assert api.get(URL).json()["count"] == 2
    gallery[0].is_published = False
    gallery[0].save()
    assert api.get(URL).json()["count"] == 1


def test_query_count_is_constant(api, gallery, make_image, django_assert_max_num_queries) -> None:
    fade = Service.objects.get(slug="fade")
    for i in range(10):
        GalleryImage.objects.create(
            category=GalleryCategory.CUTS,
            image=make_image(width=200, height=200),
            alt_text_fr=f"P{i}",
            service=fade,
        )
    with django_assert_max_num_queries(2):  # count + page with service joined
        assert api.get(URL).status_code == 200
