from django.db import models
from users.models import UserProfile, Contact
import uuid
from email.utils import parseaddr

class EmailThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='email_threads')
    subject = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    muted = models.BooleanField(
        default=False,
        help_text="Whether this whole thread was muted"
    )

    def __str__(self):
        return f"Thread: {self.subject} ({self.id})"


class Email(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
        help_text="Unique identifier for this email"
    )
    thread = models.ForeignKey(
        EmailThread,
        on_delete=models.CASCADE,
        related_name='emails',
        null=True,
        blank=True,
        help_text="The thread this email belongs to"
    )
    owner = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='emails',
        help_text="The user who owns this email"
    )

    from_email = models.CharField(
        max_length=255,
        null=True,
        help_text="Raw sender email address string"
    )
    from_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_emails',
        help_text="Sender contact linked to this email"
    )

    to_emails = models.TextField(
        blank=True,
        help_text="Raw string of recipient emails"
    )
    to_contacts = models.ManyToManyField(
        Contact,
        related_name='received_emails',
        blank=True,
        help_text="Linked recipient contacts"
    )

    message_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique message ID from the email headers"
    )
    in_reply_to = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Message-ID of the email this one is replying to"
    )

    subject = models.CharField(
        max_length=512,
        help_text="Email subject line"
    )
    body = models.TextField(
        blank=True,
        help_text="Plain text email body"
    )
    html_body = models.TextField(
        blank=True,
        help_text="HTML formatted email body"
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Whether the email has been read"
    )
    is_starred = models.BooleanField(
        default=False,
        help_text="Whether the email is marked as starred"
    )

    received_at = models.DateTimeField(
        help_text="Date and time when the email was received"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )


    def __str__(self):
        return f"Email: {self.subject} ({self.id})"


class EmailAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField(help_text="Size in bytes")
    url = models.URLField(blank=True, null=True, help_text="Link to the attachment file")

    def __str__(self):
        return self.filename
