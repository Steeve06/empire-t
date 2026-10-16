from modeltranslation.translator import TranslationOptions, register

from .models import JobOpening


@register(JobOpening)
class JobOpeningTranslation(TranslationOptions):
    fields = ("title", "requirements", "description")
