from django.contrib import admin

from .models import Agency
from .models import EndClient
from .models import MemoryCorrection
from .models import VaultCredential


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(EndClient)
class EndClientAdmin(admin.ModelAdmin):
    list_display = ("name", "agency", "slug", "created_at")
    list_filter = ("agency",)
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(VaultCredential)
class VaultCredentialAdmin(admin.ModelAdmin):
    list_display = ("service_name", "agency", "end_client", "created_at")
    list_filter = ("service_name",)
    search_fields = ("service_name",)
    readonly_fields = ("id", "created_at", "updated_at")
    exclude = ("vault_secret_id",)


@admin.register(MemoryCorrection)
class MemoryCorrectionAdmin(admin.ModelAdmin):
    list_display = ("agent_id", "corrected_by", "end_client", "created_at")
    list_filter = ("corrected_by",)
    search_fields = ("agent_id", "reason")
    readonly_fields = ("id", "created_at")
