from django import forms
from cloudinary.models import CloudinaryField
from cloudinary.forms import CloudinaryFileField
from django.contrib import admin
from django.contrib import messages
from unfold.admin import ModelAdmin, TabularInline
from .models import Contest, Block, Group, Judge, Score, FinalGroup, FinalScore, FinalResult

class ContestAdminForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.flyer:
            self.fields['flyer'].help_text = f'<img src="{self.instance.flyer.url}" style="max-height:150px;margin-top:8px;border-radius:6px;">'

class BlockInline(TabularInline):
    model = Block
    extra = 1
    fields = ("name", "order", "is_active", "is_final")


class GroupInline(TabularInline):
    model = Group
    extra = 1
    fields = ("name", "logo", "order", "qualified")


class ScoreInline(TabularInline):
    model = Score
    extra = 0
    fields = ("judge_number", "score")
    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            try:
                return max(0, obj.block.contest.judges_count - obj.scores.count())
            except Exception:
                return 4
        return 4


class FinalScoreInline(TabularInline):
    model = FinalScore
    extra = 0
    fields = ("judge_number", "score")
    can_delete = True

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            try:
                return max(0, obj.contest.final_judges_count - obj.final_scores.count())
            except Exception:
                return 4
        return 4


@admin.register(Contest)
class ContestAdmin(ModelAdmin):
    form = ContestAdminForm
    list_display  = ("name", "date", "location", "status", "judges_count", "final_judges_count", "qualifiers_per_block", "is_active")
    list_filter   = ("status", "is_active")
    list_editable = ("status", "is_active")
    search_fields = ("name", "location")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BlockInline]
    actions = ["generar_opciones_clasificados", "generar_opciones_final"]

    fieldsets = (
        ("Informacion", {"fields": ("name", "slug", "description", "flyer", "location", "date")}),
        ("Configuracion", {
            "fields": ("status", "judges_count", "final_judges_count", "qualifiers_per_block", "is_active"),
            "description": "judges_count = campos PJ en bloques. final_judges_count = campos PJ en final.",
        }),
    )

    @admin.action(description="Generar BetOptions CLASIFICADOS (desactivadas)")
    def generar_opciones_clasificados(self, request, queryset):
        from contests.services import generate_block_bet_options
        total = sum(generate_block_bet_options(c) for c in queryset)
        self.message_user(request, f"{total} opciones de clasificados creadas. Activalas desde Apuestas.", messages.SUCCESS)

    @admin.action(description="Generar BetOptions CAMPEON FINAL (desactivadas, cuotas calculadas)")
    def generar_opciones_final(self, request, queryset):
        from contests.services import generate_champion_bet_options
        total = sum(generate_champion_bet_options(c) for c in queryset)
        self.message_user(request, f"{total} opciones de campeon creadas. Revisa cuotas y activa.", messages.SUCCESS)


@admin.register(Block)
class BlockAdmin(ModelAdmin):
    list_display  = ("name", "contest", "order", "is_active", "is_final")
    list_filter   = ("contest", "is_active", "is_final")
    list_select_related = ("contest",)
    inlines = [GroupInline]


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display  = ("name", "block", "order", "get_total_score", "qualified")
    list_filter   = ("block__contest", "qualified")
    list_editable = ("qualified",)
    list_select_related = ("block", "block__contest")
    search_fields = ("name",)
    inlines = [ScoreInline]

    fieldsets = (
        ("Agrupacion", {
            "fields": ("block", "name", "logo", "order", "qualified"),
            "description": "Marcar 'Clasificado' agrega automaticamente a Tabla Final.",
        }),
    )


@admin.register(FinalGroup)
class FinalGroupAdmin(ModelAdmin):
    list_display  = ("name", "contest", "final_order", "get_total_score")
    list_filter   = ("contest",)
    list_editable = ("final_order",)
    search_fields = ("name",)
    inlines = [FinalScoreInline]

    fieldsets = (
        ("Agrupacion en Final", {
            "fields": ("contest", "name", "logo", "final_order"),
            "description": "Ajusta 'Orden en final' segun el sorteo. Agrega puntajes abajo — el podio se recalcula solo.",
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        from contests.services import rebuild_podium, refresh_champion_odds
        rebuild_podium(form.instance.contest)
        refresh_champion_odds(form.instance.contest)


@admin.register(Judge)
class JudgeAdmin(ModelAdmin):
    list_display = ("name", "contest", "judge_number")
    list_filter  = ("contest",)


@admin.register(Score)
class ScoreAdmin(ModelAdmin):
    list_display = ("group", "judge_number", "score")
    list_filter  = ("group__block__contest",)
    search_fields = ("group__name",)


@admin.register(FinalResult)
class FinalResultAdmin(ModelAdmin):
    list_display  = ("position", "group_name", "contest", "total_score")
    list_filter   = ("contest",)
    ordering      = ("contest", "position")
    readonly_fields = ("contest", "position", "group_name", "total_score", "group_logo")

    fieldsets = (
        ("Podio (generado automaticamente)", {
            "fields": ("contest", "position", "group_name", "total_score", "group_logo"),
            "description": "NO editar. Se regenera desde Tabla Final al guardar puntajes.",
        }),
    )
