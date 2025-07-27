# email_integrations/admin.py
from django.contrib import admin
from .models import GmailIntegration, OutlookIntegration, ImapIntegration

@admin.register(GmailIntegration)
class GmailIntegrationAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "is_primary", "token_expiry", "watch_channel_id")
    search_fields = ("email", "user__id", "watch_channel_id", "watch_topic_name")
    readonly_fields = ("created_at",)

@admin.register(OutlookIntegration)
class OutlookIntegrationAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "is_primary", "token_expiry")
    search_fields = ("email", "user__id")
    readonly_fields = ("created_at",)

@admin.register(ImapIntegration)
class ImapIntegrationAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "is_primary", "server", "use_ssl")
    search_fields = ("email", "server", "user__id")
    readonly_fields = ("created_at",)
    