from django.contrib import admin

from .models import ApprovedCopy
from .models import BrandVoice


@admin.register(BrandVoice)
class BrandVoiceAdmin(admin.ModelAdmin):
    list_display = ("end_client", "version", "is_active", "created_at")
    list_filter = ("is_active",)
    readonly_fields = ("id", "created_at")


@admin.register(ApprovedCopy)
class ApprovedCopyAdmin(admin.ModelAdmin):
    list_display = ("copy_type", "end_client", "campaign", "version", "is_active", "created_at")
    list_filter = ("copy_type", "is_active")
    readonly_fields = ("id", "created_at")
