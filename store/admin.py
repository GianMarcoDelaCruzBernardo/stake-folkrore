from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from .models import StoreItem, Redemption
from .services import approve_redemption, reject_redemption


@admin.register(StoreItem)
class StoreItemAdmin(ModelAdmin):
    list_display  = ("name", "price", "real_stock_display", "is_active", "order")
    list_editable = ("price", "is_active", "order")
    list_filter   = ("is_active",)
    search_fields = ("name",)
    fieldsets = (
        ("Premio", {
            "fields": ("name", "description", "image", "order", "is_active"),
        }),
        ("Precio y stock", {
            "fields": ("price", "stock"),
            "description": (
                "Precio en soles virtuales. "
                "Stock = 0 significa ilimitado (p.ej. Yapes). "
                "Stock > 0 limita la cantidad de canjes aprobados."
            ),
        }),
    )


@admin.register(Redemption)
class RedemptionAdmin(ModelAdmin):
    list_display  = ("user", "item", "cost_paid", "status", "created_at", "reviewed_at")
    list_filter   = ("status", "item")
    search_fields = ("user__username", "user__email", "full_name", "dni", "phone")
    readonly_fields = (
        "user", "item", "cost_paid", "created_at",
        "full_name", "dni", "phone", "city", "district", "address", "notes",
    )
    actions = ["aprobar_canjes", "rechazar_canjes"]

    fieldsets = (
        ("Datos del canje", {
            "fields": ("user", "item", "cost_paid", "status", "created_at"),
        }),
        ("Datos de entrega (llenados por el usuario)", {
            "fields": ("full_name", "dni", "phone", "city", "district", "address", "notes"),
        }),
        ("Gestion admin", {
            "fields": ("admin_notes", "reviewed_at"),
            "description": (
                "Usa las acciones de arriba para aprobar o rechazar. "
                "Si rechazas, el saldo SE DEVUELVE automaticamente al usuario."
            ),
        }),
    )

    @admin.action(description="Aprobar canjes seleccionados (marcar como entregado)")
    def aprobar_canjes(self, request, queryset):
        pendientes = queryset.filter(status="pending")
        count = 0
        for r in pendientes:
            approve_redemption(r)
            count += 1
        self.message_user(
            request,
            f"{count} canje(s) aprobados y marcados como entregados.",
            messages.SUCCESS,
        )

    @admin.action(description="Rechazar canjes seleccionados (devolver saldo)")
    def rechazar_canjes(self, request, queryset):
        pendientes = queryset.filter(status="pending")
        count = 0
        for r in pendientes:
            reject_redemption(r, admin_notes="Rechazado desde panel admin.")
            count += 1
        self.message_user(
            request,
            f"{count} canje(s) rechazados. Saldo devuelto a los usuarios.",
            messages.WARNING,
        )