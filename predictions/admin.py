from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Prediction, PredictionItem


class PredictionItemInline(TabularInline):
    model = PredictionItem
    extra = 0
    fields = ('category', 'block', 'predicted_group_name', 'position')


@admin.register(Prediction)
class PredictionAdmin(ModelAdmin):
    list_display = ('user', 'contest', 'get_accuracy', 'created_at')
    list_filter = ('contest',)
    inlines = [PredictionItemInline]


@admin.register(PredictionItem)
class PredictionItemAdmin(ModelAdmin):
    list_display = ('prediction', 'category', 'predicted_group_name', 'status')
    list_filter = ('category',)
