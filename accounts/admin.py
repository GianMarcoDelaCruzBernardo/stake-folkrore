from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin, UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion extra', {'fields': ('avatar', 'bio')}),
    )
