from __future__ import annotations

import datetime as dt
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.fields import HoneypotSerializerMixin
from apps.core.models import SiteSettings
from apps.core.validators import normalize_contact

from .models import ApplicationFile, JobApplication, JobOpening
from .uploads import UploadRejected, safe_original_name, validate_upload_set


class JobOpeningSerializer(serializers.ModelSerializer[JobOpening]):
    deadline = serializers.SerializerMethodField()

    class Meta:
        model = JobOpening
        fields = (
            "id",
            "slug",
            "title",
            "positions_count",
            "requirements",
            "description",
            "deadline",
        )

    def get_deadline(self, obj: JobOpening) -> dt.date | None:
        return obj.effective_deadline(self.context["site"])


class JobApplicationCreateSerializer(
    HoneypotSerializerMixin, serializers.ModelSerializer[JobApplication]
):
    opening: serializers.SlugRelatedField[JobOpening] = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=JobOpening.objects.filter(is_active=True),
        error_messages={"does_not_exist": _("Ce poste n'est plus ouvert.")},
    )
    full_name = serializers.CharField(min_length=2, max_length=100)
    contact = serializers.CharField(max_length=254)
    message = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        help_text="CV, lettre de motivation, CNI, photos ou vidéos (8 fichiers, 15 Mo chacun).",
    )

    class Meta:
        model = JobApplication
        fields = ("opening", "full_name", "contact", "message", "files", "website")

    def validate_full_name(self, value: str) -> str:
        return " ".join(value.split())

    def validate_contact(self, value: str) -> str:
        try:
            normalized, kind = normalize_contact(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages[0], code="invalid_contact") from exc
        self._contact_kind = kind
        return normalized

    def validate_opening(self, opening: JobOpening) -> JobOpening:
        site: SiteSettings = self.context["site"]
        is_open = (
            JobOpening.objects.open_on(timezone.localdate(), site).filter(pk=opening.pk).exists()
        )
        if not is_open:
            raise serializers.ValidationError(_("Les candidatures pour ce poste sont closes."))
        return opening

    def validate_files(self, files: list[Any]) -> list[Any]:
        try:
            self._file_kinds = validate_upload_set(files)
        except UploadRejected as exc:
            raise serializers.ValidationError(str(exc), code="invalid_file") from exc
        return files

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> JobApplication:
        files = validated_data.pop("files")
        application = JobApplication.objects.create(
            **validated_data,
            contact_kind=self._contact_kind,
            locale=translation.get_language() or "fr",
        )
        for upload, kind in zip(files, self._file_kinds, strict=True):
            ApplicationFile.objects.create(
                application=application,
                file=upload,
                original_name=safe_original_name(upload.name),
                kind=kind.code,
                content_type=kind.content_type,
                size=upload.size,
            )
        return application


class ApplicationReceivedSerializer(serializers.Serializer[Any]):
    detail = serializers.CharField()
