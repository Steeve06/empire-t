from modeltranslation.translator import TranslationOptions, register

from .models import Service, ServiceCategory, Supplement


@register(ServiceCategory)
class ServiceCategoryTranslation(TranslationOptions):
    fields = ("name", "title", "tagline", "booking_note")


@register(Service)
class ServiceTranslation(TranslationOptions):
    fields = ("name", "description")


@register(Supplement)
class SupplementTranslation(TranslationOptions):
    fields = ("name",)
