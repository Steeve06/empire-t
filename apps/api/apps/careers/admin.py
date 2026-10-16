from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, QuerySet
from django.http import FileResponse, HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.urls import URLPattern, path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from apps.core.admin_utils import export_as_csv, set_status_action

from .models import ApplicationFile, ApplicationStatus, JobApplication, JobOpening


def human_size(size: int) -> str:
    return f"{size / 1024 / 1024:.1f} Mo" if size >= 1024 * 1024 else f"{size / 1024:.0f} Ko"


@admin.register(JobOpening)
class JobOpeningAdmin(TranslationAdmin[JobOpening]):
    list_display = (
        "title",
        "positions_count",
        "deadline",
        "is_active",
        "application_count",
        "order",
    )
    list_editable = ("positions_count", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title_fr", "title_en", "slug")
    prepopulated_fields = {"slug": ("title_fr",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[JobOpening]:
        return super().get_queryset(request).annotate(n_applications=Count("applications"))

    @admin.display(description=_("candidatures"), ordering="n_applications")
    def application_count(self, obj: JobOpening) -> int:
        return obj.n_applications  # type: ignore[attr-defined, no-any-return]


class ApplicationFileInline(admin.TabularInline[ApplicationFile, JobApplication]):
    model = ApplicationFile
    extra = 0
    can_delete = False
    fields = ("download_link", "kind", "size_label", "uploaded_at")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    @admin.display(description=_("fichier"))
    def download_link(self, obj: ApplicationFile) -> SafeString:
        url = reverse("admin:careers_applicationfile_download", args=[obj.pk])
        return format_html('<a href="{}">{} ⬇</a>', url, obj.original_name)

    @admin.display(description=_("taille"))
    def size_label(self, obj: ApplicationFile) -> str:
        return human_size(obj.size)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin[JobApplication]):
    list_display = ("full_name", "opening", "contact", "file_count", "status", "created_at")
    list_filter = ("status", "opening", "contact_kind", "created_at")
    list_select_related = ("opening",)
    search_fields = ("full_name", "contact")
    date_hierarchy = "created_at"
    readonly_fields = (
        "opening",
        "full_name",
        "contact",
        "contact_kind",
        "message",
        "locale",
        "created_at",
        "files_summary",
    )
    fields = (
        "status",
        "opening",
        "full_name",
        "contact",
        "contact_kind",
        "message",
        "internal_notes",
        "locale",
        "created_at",
    )
    inlines = (ApplicationFileInline,)
    actions = (
        set_status_action(ApplicationStatus.REVIEWING, _("Marquer « en cours d'examen »")),
        set_status_action(ApplicationStatus.INTERVIEW, _("Marquer « entretien prévu »")),
        set_status_action(ApplicationStatus.REJECTED, _("Marquer « non retenue »")),
        set_status_action(ApplicationStatus.HIRED, _("Marquer « recruté(e) »")),
        export_as_csv(
            (
                ("Nom", "full_name"),
                ("Poste", lambda a: a.opening.title_fr),
                ("Contact", "contact"),
                ("Statut", lambda a: a.get_status_display()),
                ("Reçue le", lambda a: a.created_at.strftime("%d/%m/%Y %H:%M")),
            ),
            "candidatures",
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[JobApplication]:
        return super().get_queryset(request).annotate(n_files=Count("files"))

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.display(description=_("fichiers"), ordering="n_files")
    def file_count(self, obj: JobApplication) -> int:
        return obj.n_files  # type: ignore[attr-defined, no-any-return]

    @admin.display(description=_("pièces jointes"))
    def files_summary(self, obj: JobApplication) -> SafeString:
        return format_html_join(", ", "{}", ((f.original_name,) for f in obj.files.all()))

    def get_urls(self) -> list[URLPattern]:
        download = path(
            "files/<int:file_id>/download/",
            self.admin_site.admin_view(self.download_file),
            name="careers_applicationfile_download",
        )
        return [download, *super().get_urls()]

    def download_file(self, request: HttpRequest, file_id: int) -> HttpResponseBase:
        """Staff-only download: private files are never exposed under /media/."""
        if not self.has_view_permission(request):
            raise PermissionDenied
        attachment = get_object_or_404(ApplicationFile, pk=file_id)
        storage = attachment.file.storage
        if isinstance(storage, FileSystemStorage):
            return FileResponse(
                attachment.file.open("rb"),
                as_attachment=True,
                filename=attachment.original_name,
                content_type=attachment.content_type,
            )
        # Object storage: short-lived signed URL (querystring_expire in prod settings)
        return HttpResponseRedirect(storage.url(attachment.file.name))
