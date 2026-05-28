from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(ModelAdmin):
    list_display  = ("user", "contest", "champion", "status", "created_at")
    list_filter   = ("contest",)
    search_fields = ("user__username", "user__email", "champion__name")
    readonly_fields = ("user", "contest", "champion", "created_at", "updated_at")

    def status(self, obj):
        return obj.status()
    status.short_description = "Estado"