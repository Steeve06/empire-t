from modeltranslation.translator import TranslationOptions, register

from .models import SiteSettings, TeamMember, Testimonial


@register(SiteSettings)
class SiteSettingsTranslation(TranslationOptions):
    fields = (
        "tagline",
        "address_line",
        "opening_days_label",
        "application_documents",
        "story",
        "amenities",
    )


@register(Testimonial)
class TestimonialTranslation(TranslationOptions):
    fields = ("quote",)


@register(TeamMember)
class TeamMemberTranslation(TranslationOptions):
    fields = ("role", "bio")
