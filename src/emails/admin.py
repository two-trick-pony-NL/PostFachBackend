from django.contrib import admin
from .models import EmailThread, Email, EmailAttachment
from users.models import Contact

@admin.register(EmailThread)
class EmailThreadAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'created_at')
    search_fields = ('subject',)
    list_filter = ('created_at', 'owner')


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'from_contact', 'is_read', 'is_starred', 'received_at')
    search_fields = ('subject', 'message_id', 'body')
    list_filter = ('is_read', 'is_starred', 'received_at', 'owner')
    raw_id_fields = ('from_contact', 'owner', 'thread')
    filter_horizontal = ('to_contacts',)


@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'email', 'mime_type', 'size')
    search_fields = ('filename', 'mime_type')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'display_name', 'owner', 'always_notify', 'muted', 'important', 'whitelist')
    search_fields = ('email', 'display_name')
    list_filter = ('always_notify', 'muted', 'marked_as_spam', 'important', 'whitelist')
    raw_id_fields = ('owner',)
