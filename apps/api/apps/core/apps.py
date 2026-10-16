from typing import Any

from django.apps import AppConfig
from django.db.models import Model
from django.db.models.signals import post_delete, post_save


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Site"

    def ready(self) -> None:
        from .cache import invalidate_on_content_change
        from .models import OptimizedImagesModel

        post_save.connect(invalidate_on_content_change, dispatch_uid="api-cache-save")
        post_delete.connect(invalidate_on_content_change, dispatch_uid="api-cache-delete")

        def delete_image_files(sender: type[Model], instance: Model, **_: Any) -> None:
            if isinstance(instance, OptimizedImagesModel):
                instance.delete_image_files()

        post_delete.connect(delete_image_files, weak=False, dispatch_uid="delete-image-variants")
