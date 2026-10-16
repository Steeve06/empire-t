import logging
from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_delete

logger = logging.getLogger(__name__)


class CareersConfig(AppConfig):
    name = "apps.careers"
    verbose_name = "Recrutement"

    def ready(self) -> None:
        from .models import ApplicationFile

        def delete_stored_file(
            sender: type[ApplicationFile], instance: ApplicationFile, **_: Any
        ) -> None:
            if instance.file:
                try:
                    instance.file.delete(save=False)
                except OSError:
                    logger.warning("Could not delete %s", instance.file.name, exc_info=True)

        post_delete.connect(
            delete_stored_file,
            sender=ApplicationFile,
            weak=False,
            dispatch_uid="delete-application-file",
        )
