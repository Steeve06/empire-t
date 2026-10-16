from modeltranslation.translator import TranslationOptions, register

from .models import GalleryImage


@register(GalleryImage)
class GalleryImageTranslation(TranslationOptions):
    fields = ("alt_text", "caption")
