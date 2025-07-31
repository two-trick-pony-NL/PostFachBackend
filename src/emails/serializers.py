# serializers.py

from rest_framework import serializers
from .models import Email, EmailThread, Contact, EmailAttachment
from users.serializers import ContactSerializer
from rest_framework.reverse import reverse



class EmailAttachmentSerializer(serializers.ModelSerializer):
    private_file_url = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()  # changed here
    share_url_expiry = serializers.ReadOnlyField()

    class Meta:
        model = EmailAttachment
        fields = [
            'id',
            'filename',
            'mime_type',
            'size',
            'download_count',
            'share_url_expiry',
            'created_at',
            'updated_at',
            'share_url',
            'private_file_url',
        ]

    def get_private_file_url(self, obj):
        request = self.context.get('request')
        if request:
            return reverse('attachment-download', kwargs={'id': obj.id}, request=request)
        return None

    def get_share_url(self, obj):
        request = self.context.get('request')
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
            return f"{base_url}{obj.share_url}"
        return None




class EmailInThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            'id', 'from_email', 'subject', 'body', 'sanitized_html_body',
            'is_read', 'is_starred', 'received_at'
        ]


class EmailThreadSerializer(serializers.ModelSerializer):
    emails = EmailInThreadSerializer(many=True, read_only=True)

    class Meta:
        model = EmailThread
        fields = ['id', 'subject', 'created_at', 'emails']


class EmailSerializer(serializers.ModelSerializer):
    from_contact = ContactSerializer(read_only=True)
    to_contacts = ContactSerializer(many=True, read_only=True)
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    thread = EmailThreadSerializer(read_only=True)

    # Updatable fields
    is_read = serializers.BooleanField(required=False)
    is_starred = serializers.BooleanField(required=False)
    is_archived = serializers.BooleanField(required=False)
    is_snoozed = serializers.BooleanField(required=False)
    snoozed_until = serializers.DateTimeField(required=False, allow_null=True)
    is_trashed = serializers.BooleanField(required=False)
    is_pinned = serializers.BooleanField(required=False)
    

    class Meta:
        model = Email
        fields = [
            'id', 'status', 'thread', 'direction', 'owner', 'from_email', 'from_contact', 'to_contacts',
            'message_id', 'in_reply_to', 'subject', 'body', 'sanitized_html_body',
            'is_read', 'is_starred',
            'is_archived', 'is_snoozed', 'snoozed_until',
            'is_trashed', 'is_pinned',
            'received_at', 'created_at', 'updated_at',
            'attachments',
        ]
        read_only_fields = [
            'id', 'status', 'owner', 'direction', 'from_email', 'from_contact', 'to_contacts',
            'message_id', 'in_reply_to', 'subject', 'body', 'sanitized_html_body',
            'received_at', 'created_at', 'updated_at', 'attachments', 'thread',
        ]

class SendEmailSerializer(serializers.Serializer):
    integration_id = serializers.UUIDField()
    to_emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False
    )
    subject = serializers.CharField()
    body_text = serializers.CharField()
    body_html = serializers.CharField(required=False, allow_blank=True)
    from_name = serializers.CharField(required=False, allow_blank=True)