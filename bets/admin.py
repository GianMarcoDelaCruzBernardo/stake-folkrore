from django.contrib import admin
from django.contrib import messages
from unfold.admin import ModelAdmin, TabularInline
from decimal import Decimal
from .models import Wallet, BetOption, Bet


class BetInline(TabularInline):
    model = Bet
    extra = 0
    readonly_fields = ("user", "amount", "odds_at_bet", "potential_win", "status", "placed_at")
    can_delete = False
    fields = ("user", "amount", "odds_at_bet", "potential_win", "status", "placed_at")


@admin.register(BetOption)
class BetOptionAdmin(ModelAdmin):
    list_display  = ("group_name", "contest", "get_bet_type_display", "block", "odds", "is_active", "is_resolved", "won")
    list_filter   = ("contest", "bet_type", "is_active", "is_resolved")
    list_editable = ("odds", "is_active")
    search_fields = ("group_name",)
    inlines = [BetInline]
    actions = ["activar", "desactivar", "gen_clasificados", "gen_campeon", "limpiar_pendientes"]

    fieldsets = (
        ("Configuracion", {
            "fields": ("contest", "bet_type", "block", "group_name", "group_logo", "odds", "is_active"),
            "description": "Clasificados: cuota 1.53 fija. Campeon: edita la cuota. Activa cuando quieras.",
        }),
        ("Resultado", {"fields": ("is_resolved", "won")}),
    )

    @admin.action(description="Activar seleccionadas")
    def activar(self, request, qs):
        n = qs.update(is_active=True)
        self.message_user(request, f"{n} opciones activadas.", messages.SUCCESS)

    @admin.action(description="Desactivar seleccionadas")
    def desactivar(self, request, qs):
        n = qs.update(is_active=False)
        self.message_user(request, f"{n} opciones desactivadas.", messages.SUCCESS)

    @admin.action(description="Generar opciones CLASIFICADOS para estos concursos")
    def gen_clasificados(self, request, qs):
        from contests.services import generate_block_bet_options
        ids = qs.values_list("contest_id", flat=True).distinct()
        from contests.models import Contest
        total = sum(generate_block_bet_options(Contest.objects.get(pk=i)) for i in ids)
        self.message_user(request, f"{total} opciones creadas.", messages.SUCCESS)

    @admin.action(description="Generar opciones CAMPEON para estos concursos")
    def gen_campeon(self, request, qs):
        from contests.services import generate_champion_bet_options
        ids = qs.values_list("contest_id", flat=True).distinct()
        from contests.models import Contest
        total = sum(generate_champion_bet_options(Contest.objects.get(pk=i)) for i in ids)
        self.message_user(request, f"{total} opciones campeon creadas.", messages.SUCCESS)

    @admin.action(description="Eliminar apuestas PENDIENTES y devolver saldo")
    def limpiar_pendientes(self, request, qs):
        bets = Bet.objects.filter(option__in=qs, status="pending").select_related("user")
        count = 0
        for bet in bets:
            wallet, _ = Wallet.objects.get_or_create(user=bet.user)
            wallet.balance += bet.amount
            wallet.save(update_fields=["balance"])
            count += 1
        bets.delete()
        self.message_user(request, f"{count} apuestas eliminadas y saldo devuelto.", messages.SUCCESS)


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display  = ("user", "balance", "total_won", "total_lost")
    readonly_fields = ("total_won", "total_lost")
    search_fields = ("user__username", "user__email")
    actions = ["reset_saldo"]

    @admin.action(description="Resetear saldo a S/50")
    def reset_saldo(self, request, qs):
        qs.update(balance=Decimal("50.00"))
        self.message_user(request, "Saldo reseteado.", messages.SUCCESS)


@admin.register(Bet)
class BetAdmin(ModelAdmin):
    list_display  = ("user", "option", "amount", "odds_at_bet", "potential_win", "status", "placed_at")
    list_filter   = ("status", "option__contest")
    readonly_fields = ("potential_win", "placed_at", "resolved_at")
    search_fields = ("user__username",)
