"""Initial content for Empire T, in French and English. Loaded by ``manage.py seed``.

Prices are in FCFA. ``price=None`` with ``on_quote=True`` means « sur devis ».
Durations are (min, max) in minutes; max is None for a fixed duration.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class T:
    """A translated string."""

    fr: str
    en: str


@dataclass(frozen=True)
class ServiceSeed:
    slug: str
    name: T
    duration: tuple[int, int | None]
    price: int | None
    from_price: bool = False
    on_quote: bool = False
    popular: bool = False
    description: T = field(default_factory=lambda: T("", ""))


@dataclass(frozen=True)
class CategorySeed:
    slug: str
    name: T
    title: T
    tagline: T
    accent: str
    services: tuple[ServiceSeed, ...]
    booking_note: T = field(default_factory=lambda: T("", ""))
    appointment_only: bool = False
    show_on_home: bool = True


@dataclass(frozen=True)
class SupplementSeed:
    name: T
    price: int
    from_price: bool = False


@dataclass(frozen=True)
class OpeningSeed:
    slug: str
    title: T
    positions: int
    requirements: T


CATEGORIES: tuple[CategorySeed, ...] = (
    CategorySeed(
        slug="men",
        name=T("Hommes", "Men"),
        title=T("Barbershop Hommes", "Men's Barbershop"),
        tagline=T("Fades, tapers, barbe et finitions.", "Fades, tapers, beard work and finishing."),
        accent="gold",
        services=(
            ServiceSeed(
                "coupe-simple", T("Coupe simple", "Classic haircut"), (20, None), 1000, popular=True
            ),
            ServiceSeed(
                "contours-line-up", T("Contours / Line up", "Line up / edges"), (10, 15), 500
            ),
            ServiceSeed(
                "taper",
                T("Taper (bas, moyen, haut, drop)", "Taper (low, mid, high, drop)"),
                (20, 30),
                1500,
            ),
            ServiceSeed(
                "fade",
                T("Low, Mid, High Fade", "Low, mid or high fade"),
                (30, None),
                1500,
                popular=True,
            ),
            ServiceSeed("skin-fade", T("Skin Fade", "Skin fade"), (35, 40), 2000),
            ServiceSeed("afro-fade", T("Afro + Fade", "Afro + fade"), (35, None), 2000),
            ServiceSeed("waves-fade", T("Waves + Fade", "Waves + fade"), (40, None), 2000),
            ServiceSeed("fade-design", T("Fade + design", "Fade + design"), (35, 40), 2000),
            ServiceSeed("french-crop", T("French crop", "French crop"), (35, None), 1800),
        ),
    ),
    CategorySeed(
        slug="women",
        name=T("Femmes", "Women"),
        title=T("Coiffure Femmes", "Women's Hair"),
        tagline=T("Nattes, twists, locks et entretien.", "Cornrows, twists, locs and upkeep."),
        booking_note=T("Sur rendez-vous", "By appointment"),
        appointment_only=True,
        accent="gold",
        services=(
            ServiceSeed(
                "twists-vanilles", T("Twists / Vanilles", "Twists"), (60, 90), 3000, from_price=True
            ),
            ServiceSeed(
                "nattes-cornrows",
                T("Nattes / Cornrows", "Cornrows / braids"),
                (60, 90),
                3500,
                from_price=True,
                popular=True,
            ),
            ServiceSeed(
                "locks",
                T("Locks, installation et entretien", "Locs, installation and upkeep"),
                (60, 120),
                4000,
                from_price=True,
            ),
            ServiceSeed("retwist", T("Retwist", "Retwist"), (60, 90), 4000, from_price=True),
            ServiceSeed(
                "locks-complexes",
                T("Locks complexes", "Complex locs"),
                (120, 240),
                None,
                on_quote=True,
                description=T(
                    "Tarif établi après un échange sur le style souhaité.",
                    "Priced after a quick chat about the style you want.",
                ),
            ),
        ),
    ),
    CategorySeed(
        slug="kids",
        name=T("Enfants", "Kids"),
        title=T("Enfants", "Kids"),
        tagline=T("Coupes et tresses jusqu'à 12 ans.", "Haircuts and braids up to age 12."),
        accent="gold",
        services=(
            ServiceSeed(
                "coupe-enfant",
                T("Coupe enfant, jusqu'à 12 ans", "Kids haircut, up to age 12"),
                (20, None),
                1000,
            ),
            ServiceSeed(
                "coiffure-enfant",
                T("Coiffures enfant, tresses", "Kids hairstyles, braids"),
                (30, 60),
                2000,
                from_price=True,
            ),
        ),
    ),
    CategorySeed(
        slug="beauty",
        name=T("Beauty & Spa", "Beauty & Spa"),
        title=T("Beauty & Spa", "Beauty & Spa"),
        tagline=T(
            "Ongles, pédicure, soins du visage, maquillage.",
            "Nails, pedicure, facials and make-up.",
        ),
        accent="rose",
        services=(
            ServiceSeed(
                "manucure",
                T("Ongles / Manucure", "Nails / manicure"),
                (40, 60),
                2000,
                from_price=True,
            ),
            ServiceSeed("pedicure", T("Pédicure", "Pedicure"), (45, 60), 2500, from_price=True),
            ServiceSeed(
                "soins-visage",
                T("Soins du visage", "Facial treatment"),
                (45, None),
                3000,
                from_price=True,
            ),
            ServiceSeed("maquillage", T("Maquillage", "Make-up"), (45, 60), 3000, from_price=True),
        ),
    ),
    CategorySeed(
        slug="packs",
        name=T("Barbe & Packs", "Beard & Packages"),
        title=T("Barbe & Packs", "Beard & Packages"),
        tagline=T(
            "Barbe, coupe + barbe et le forfait Empire Premium.",
            "Beard care, haircut + beard and the Empire Premium package.",
        ),
        accent="gold",
        show_on_home=False,
        services=(
            ServiceSeed(
                "barbe", T("Taille + contours barbe", "Beard trim + line up"), (15, None), 1000
            ),
            ServiceSeed(
                "coupe-barbe", T("Coupe + barbe", "Haircut + beard"), (40, 45), 2500, popular=True
            ),
            ServiceSeed(
                "empire-premium",
                T("Empire Premium", "Empire Premium"),
                (50, 60),
                3500,
                description=T(
                    "Coupe, taille de barbe, serviette chaude et soin du visage. "
                    "Le rituel complet.",
                    "Haircut, beard trim, hot towel and facial. The complete ritual.",
                ),
            ),
        ),
    ),
)

SIGNATURE_SERVICE_SLUG = "empire-premium"

SUPPLEMENTS: tuple[SupplementSeed, ...] = (
    SupplementSeed(T("Massage du cuir chevelu", "Scalp massage"), 1000),
    SupplementSeed(T("Serviette chaude", "Hot towel"), 500),
    SupplementSeed(T("Rasage complet", "Full shave"), 1500),
    SupplementSeed(T("Coloration", "Colouring"), 3000, from_price=True),
)

OPENINGS: tuple[OpeningSeed, ...] = (
    OpeningSeed(
        "barber-titulaire",
        T("Barber titulaire", "Permanent barber"),
        2,
        T(
            "2 ans d'expérience minimum, maîtrise des dégradés (fades) et de la barbe.",
            "At least 2 years of experience, confident with fades and beard work.",
        ),
    ),
    OpeningSeed(
        "barber-remplacant",
        T("Barber remplaçant", "Relief barber"),
        3,
        T("1 an d'expérience minimum.", "At least 1 year of experience."),
    ),
    OpeningSeed(
        "estheticienne-titulaire",
        T("Esthéticienne titulaire", "Permanent beautician"),
        1,
        T("Soins du visage, ongles et massage.", "Facials, nails and massage."),
    ),
    OpeningSeed(
        "estheticienne-remplacante",
        T("Esthéticienne remplaçante", "Relief beautician"),
        3,
        T("Expérience en esthétique.", "Experience in beauty care."),
    ),
)

SITE = {
    "business_name": "Empire T",
    "business_subtitle": "Barbershop & Beauty",
    "whatsapp_number": "+237653147512",
    "email": "contact@empire-t.cm",
    "city": "Yaoundé",
    "country_code": "CM",
    "opening_time": dt.time(7, 0),
    "closing_time": dt.time(21, 0),
    "latitude": Decimal("3.893500"),
    "longitude": Decimal("11.544000"),
    "recruitment_deadline": dt.date(2026, 11, 15),
}

SITE_TRANSLATED: dict[str, T] = {
    "tagline": T("Plus qu'une coupe, une expérience.", "More than a haircut, an experience."),
    "address_line": T(
        "Nkolmesseng, axe principal, à côté du carrefour",
        "Nkolmesseng, main road, next to the crossroads",
    ),
    "opening_days_label": T("Ouvert 7j/7", "Open 7 days a week"),
    "application_documents": T(
        "Lettre de motivation\nCV actualisé\nCopie de la CNI\n"
        "Photos ou vidéos de vos réalisations\nRéférences professionnelles (si disponibles)",
        "Cover letter\nUp-to-date CV\nCopy of your national ID card (CNI)\n"
        "Photos or videos of your work\nProfessional references (if available)",
    ),
    "story": T(
        "Empire T est né d'une idée simple : offrir au quartier de Nkolmesseng un salon où la "
        "précision du barbier rencontre l'art de la coiffure et du bien-être. Hommes, femmes et "
        "enfants y trouvent le même niveau d'exigence : du matériel désinfecté après chaque "
        "client, des gestes maîtrisés et un accueil qui donne envie de revenir.\n\n"
        "Avec ou sans rendez-vous, sept jours sur sept, notre équipe prend le temps de "
        "comprendre votre style pour vous offrir plus qu'une coupe : une expérience.",
        "Empire T was born from a simple idea: to give Nkolmesseng a salon where a barber's "
        "precision meets the art of hairstyling and well-being. Men, women and children all get "
        "the same high standard: tools disinfected after every client, skilled hands and a "
        "welcome that makes you want to come back.\n\n"
        "With or without an appointment, seven days a week, our team takes the time to "
        "understand your style and give you more than a haircut: an experience.",
    ),
    "amenities": T(
        "Wi-Fi gratuit\nClimatisation\nMusique et TV\nAire d'attente confortable\n"
        "Paiement Mobile Money",
        "Free Wi-Fi\nAir conditioning\nMusic and TV\nComfortable waiting area\n"
        "Mobile Money payments",
    ),
}
