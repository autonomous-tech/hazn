from django.contrib import admin

from .models import Audit
from .models import Campaign
from .models import Decision
from .models import Keyword


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("term", "end_client", "search_volume", "difficulty", "status")
    list_filter = ("status", "intent")
    search_fields = ("term",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("audit_type", "end_client", "score", "created_at")
    list_filter = ("audit_type",)
    readonly_fields = ("id", "created_at")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "end_client", "campaign_type", "status", "created_at")
    list_filter = ("status", "campaign_type")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ("decision_type", "end_client", "campaign", "created_at")
    list_filter = ("decision_type",)
    readonly_fields = ("id", "created_at")
