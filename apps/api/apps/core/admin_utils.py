"""Reusable admin pieces: image previews, CSV export and status-change actions."""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from django.contrib import admin, messages
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from .models import OptimizedImagesModel

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise

AdminAction = Callable[[admin.ModelAdmin[Any], HttpRequest, QuerySet[Any]], Any]


def image_preview(obj: OptimizedImagesModel, field_name: str, height: int = 64) -> SafeString:
    meta = obj.image_meta.get(field_name)
    if not meta:
        return format_html('<span style="color:#999">{}</span>', _("Aucune photo"))
    smallest = meta["variants"][0]["name"]
    url = getattr(obj, field_name).storage.url(smallest)
    return format_html(
        '<img src="{}" alt="" style="height:{}px;width:auto;border-radius:4px;'
        'object-fit:cover;border:1px solid #e4ddd0">',
        url,
        height,
    )


def export_as_csv(
    columns: Iterable[tuple[str, str | Callable[[Any], Any]]], filename_prefix: str
) -> AdminAction:
    """Build an admin action exporting ``columns`` (header, attribute or callable) to CSV."""
    columns = list(columns)

    @admin.action(description=_("Exporter la sélection (CSV)"))
    def action(
        modeladmin: admin.ModelAdmin[Any], request: HttpRequest, queryset: QuerySet[Any]
    ) -> HttpResponse:
        stamp = timezone.localtime().strftime("%Y%m%d-%H%M")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename_prefix}-{stamp}.csv"'
        response.write("﻿")  # BOM so Excel opens accents correctly
        writer = csv.writer(response, delimiter=";")
        writer.writerow([header for header, _ in columns])
        for obj in queryset:
            writer.writerow(
                [value(obj) if callable(value) else getattr(obj, value) for _, value in columns]
            )
        return response

    action.__name__ = "export_as_csv"
    return action


def set_status_action(status: str, label: StrOrPromise) -> AdminAction:
    """Admin action moving the selected rows to ``status``, one save() per row."""

    @admin.action(description=label)
    def action(
        modeladmin: admin.ModelAdmin[Any], request: HttpRequest, queryset: QuerySet[Model]
    ) -> None:
        updated = 0
        for obj in queryset:
            if getattr(obj, "status", None) != status:
                obj.status = status  # type: ignore[attr-defined]
                obj.save(update_fields=["status", "updated_at"])
                updated += 1
        modeladmin.message_user(
            request, _("%(count)d élément(s) mis à jour.") % {"count": updated}, messages.SUCCESS
        )

    action.__name__ = f"set_status_{status}"
    return action
