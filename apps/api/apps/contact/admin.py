from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from apps.core.admin_utils import set_status_action
from apps.core.models import ContactKind
from apps.core.whatsapp import whatsapp_link

from .models import ContactMessage, MessageStatus


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin[ContactMessage]):
    list_display = ("name", "reply_link", "excerpt", "status", "created_at")
    list_filter = ("status", "contact_kind", "created_at")
    search_fields = ("name", "contact", "message")
    date_hierarchy = "created_at"
    readonly_fields = (
        "name",
        "contact",
        "contact_kind",
        "reply_link",
        "message",
        "locale",
        "created_at",
    )
    fields = ("status", "name", "contact", "reply_link", "message", "locale", "created_at")
    actions = (
        set_status_action(MessageStatus.READ, _("Marquer comme lus")),
        set_status_action(MessageStatus.ANSWERED, _("Marquer comme répondus")),
        set_status_action(MessageStatus.ARCHIVED, _("Archiver")),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def change_view(self, request: HttpRequest, object_id: str, *args: Any, **kwargs: Any) -> Any:
        ContactMessage.objects.filter(pk=object_id, status=MessageStatus.NEW).update(
            status=MessageStatus.READ
        )
        return super().change_view(request, object_id, *args, **kwargs)

    @admin.display(description=_("répondre"))
    def reply_link(self, obj: ContactMessage) -> SafeString:
        if obj.contact_kind == ContactKind.EMAIL:
            href = f"mailto:{obj.contact}?subject=Empire%20T"
        else:
            href = whatsapp_link(obj.contact, f"Bonjour {obj.name}, ici Empire T. ")
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{} ↗</a>', href, obj.contact
        )

    @admin.display(description=_("message"))
    def excerpt(self, obj: ContactMessage) -> str:
        return obj.message if len(obj.message) <= 80 else f"{obj.message[:77]}…"
