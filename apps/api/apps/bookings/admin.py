from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from apps.core.admin_utils import export_as_csv, set_status_action
from apps.core.validators import format_cameroon_display

from .models import BookingRequest, BookingStatus
from .services import customer_whatsapp_url

STATUS_COLORS = {
    BookingStatus.NEW: "#b8923a",
    BookingStatus.CONFIRMED: "#2e7d32",
    BookingStatus.COMPLETED: "#546e7a",
    BookingStatus.CANCELLED: "#c62828",
    BookingStatus.NO_SHOW: "#6d4c41",
}


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin[BookingRequest]):
    list_display = (
        "reference",
        "date",
        "time_label",
        "customer_name",
        "whatsapp_reply",
        "service_name",
        "status_badge",
        "channel",
        "created_at",
    )
    list_filter = ("status", "date", "service__category", "channel", "locale")
    list_select_related = ("service",)
    search_fields = ("reference", "customer_name", "phone", "service_name")
    date_hierarchy = "date"
    ordering = ("-date", "-time_slot")
    list_per_page = 50
    autocomplete_fields = ("service",)
    readonly_fields = (
        "reference",
        "service_name",
        "price_snapshot",
        "price_is_from",
        "duration_minutes",
        "locale",
        "channel",
        "created_at",
        "updated_at",
        "whatsapp_reply",
    )
    fieldsets = (
        (
            _("Demande"),
            {"fields": ("reference", "status", "service", "service_name", "date", "time_slot")},
        ),
        (_("Client"), {"fields": ("customer_name", "phone", "whatsapp_reply", "notes")}),
        (
            _("Tarif et paiement"),
            {
                "fields": (
                    "price_snapshot",
                    "price_is_from",
                    "duration_minutes",
                    "payment_status",
                    "amount_due",
                    "payment_reference",
                )
            },
        ),
        (
            _("Suivi interne"),
            {"fields": ("internal_notes", "channel", "locale", "created_at", "updated_at")},
        ),
    )
    actions = (
        set_status_action(BookingStatus.CONFIRMED, _("Marquer comme confirmées")),
        set_status_action(BookingStatus.COMPLETED, _("Marquer comme honorées")),
        set_status_action(BookingStatus.CANCELLED, _("Marquer comme annulées")),
        set_status_action(BookingStatus.NO_SHOW, _("Marquer comme absents")),
        export_as_csv(
            (
                ("Référence", "reference"),
                ("Date", "date"),
                ("Heure", lambda b: b.time_slot.strftime("%H:%M")),
                ("Client", "customer_name"),
                ("Téléphone", "phone"),
                ("Prestation", "service_name"),
                ("Prix", "price_snapshot"),
                ("Statut", lambda b: b.get_status_display()),
                ("Créée le", lambda b: b.created_at.strftime("%d/%m/%Y %H:%M")),
            ),
            "reservations",
        ),
    )

    @admin.display(description=_("heure"), ordering="time_slot")
    def time_label(self, obj: BookingRequest) -> str:
        return obj.time_slot.strftime("%Hh%M")

    @admin.display(description=_("WhatsApp client"))
    def whatsapp_reply(self, obj: BookingRequest) -> SafeString | str:
        if not obj.pk:
            return "-"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" title="{}">{} ↗</a>',
            customer_whatsapp_url(obj),
            _("Ouvrir WhatsApp avec un message de confirmation"),
            format_cameroon_display(obj.phone),
        )

    @admin.display(description=_("statut"), ordering="status")
    def status_badge(self, obj: BookingRequest) -> SafeString:
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;'
            'font-size:11px;white-space:nowrap">{}</span>',
            STATUS_COLORS.get(BookingStatus(obj.status), "#666"),
            obj.get_status_display(),
        )
