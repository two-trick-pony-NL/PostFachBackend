# serializers.py

from rest_framework import serializers
from .models import Email, EmailThread, Contact, EmailAttachment
from users.serializers import ContactSerializer


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = ['id', 'filename', 'mime_type', 'size', 'url']


class EmailInThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            'id', 'from_email', 'subject', 'body', 'html_body',
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

    # Fields allowed to update
    is_read = serializers.BooleanField(required=False)
    is_starred = serializers.BooleanField(required=False)

    class Meta:
        model = Email
        fields = [
            'id', 'thread', 'owner', 'from_email', 'from_contact', 'to_emails', 'to_contacts',
            'message_id', 'in_reply_to', 'subject', 'body', 'html_body',
            'is_read', 'is_starred',
            'received_at', 'created_at', 'updated_at',
            'attachments',
        ]
        read_only_fields = [
            'id', 'owner', 'from_email', 'from_contact', 'to_emails', 'to_contacts',
            'message_id', 'in_reply_to', 'subject', 'body', 'html_body',
            'received_at', 'created_at', 'updated_at', 'attachments', 'thread',
        ]
