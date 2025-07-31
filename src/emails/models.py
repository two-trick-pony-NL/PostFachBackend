from django.db import models
from users.models import UserProfile, Contact
import uuid
from email.utils import parseaddr
import bleach
from django.utils import timezone



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
    DIRECTION_CHOICES = [
        ("IN", "Incoming"),
        ("OUT", "Outgoing"),
        
        
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('received', 'Received'),
        ('queued', 'Queued'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
        ('trashed', 'Trashed'),
        ('snoozed', 'Snoozed'),
    ]

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
        help_text="Unique identifier for this email"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='received',
        help_text="Status of the email"
    )
    direction = models.CharField(
        max_length=3,
        choices=DIRECTION_CHOICES,
        default="IN",
        help_text="Direction of the email relative to the user"
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

    to_contacts = models.ManyToManyField(
        Contact,
        related_name='received_emails',
        blank=True,
        help_text="Linked 'To' recipient contacts"
    )
    cc_contacts = models.ManyToManyField(
        Contact,
        related_name='cced_emails',
        blank=True,
        help_text="Linked 'CC' recipient contacts"
    )
    bcc_contacts = models.ManyToManyField(
        Contact,
        related_name='bcced_emails',
        blank=True,
        help_text="Linked 'BCC' recipient contacts"
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
    is_archived = models.BooleanField(default=False)
    is_snoozed = models.BooleanField(default=False)
    snoozed_until = models.DateTimeField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)   # optional, like "Pin to top"
    is_replied = models.BooleanField(default=False)  # optional, for UX
    is_draft = models.BooleanField(default=False)    
    
    def sanitized_html_body(self):
        allowed_tags = ['p', 'b', 'i', 'u', 'a', 'br', 'ul', 'ol', 'li', 'strong', 'em']
        allowed_attrs = {
            'a': ['href', 'title', 'rel'],
        }
        return bleach.clean(self.html_body or '', tags=allowed_tags, attributes=allowed_attrs, strip=True)


    def __str__(self):
        return f"Email: {self.subject} ({self.id})"



class EmailAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='email_attachments')
    email = models.ForeignKey('Email', on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField(help_text="Size in bytes")
    url = models.URLField(blank=True, null=True, help_text="Link to the attachment file")
    file = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Public token for accessing this attachment")
    public_token_created = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.filename
    
    @property
    def share_url(self):
        user_id = str(self.email.owner.id)
        return f"/api/emails/attachments/shared/{user_id}-{self.public_token}/"
    
    @property
    def share_url_expiry(self):
        return self.public_token_created + timezone.timedelta(days=7)

    def rotate_token(self): #Rotates the public token and resets the download count
        self.public_token = uuid.uuid4()
        self.public_token_created = timezone.now()
        self.download_count = 0
        self.save(update_fields=['public_token', 'public_token_created', 'download_count'])
