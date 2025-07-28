from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
import uuid
from users.models import UserProfile
from django.core.validators import MinValueValidator
from django_rq import get_scheduler

class BaseEmailIntegration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)  # NO related_name here
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class GmailIntegration(BaseEmailIntegration):
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField()
    token_expiry = models.DateTimeField()
    
    # Watch info
    watch_channel_id = models.CharField(max_length=255, blank=True, null=True)
    watch_resource_id = models.CharField(max_length=255, blank=True, null=True)
    watch_expiration = models.BigIntegerField(blank=True, null=True)
    watch_topic_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Gmail: {self.email}"

class OutlookIntegration(BaseEmailIntegration):
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField()
    tenant_id = EncryptedCharField(max_length=255)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return f"Outlook: {self.email}"

class ImapIntegration(BaseEmailIntegration):
    # IMAP connection
    server = EncryptedCharField(max_length=255)
    port = models.PositiveIntegerField()
    username = EncryptedCharField(max_length=255)
    password = EncryptedCharField(max_length=255)
    use_ssl = models.BooleanField(default=True)
    refresh_interval_seconds = models.PositiveIntegerField(default=900, validators=[MinValueValidator(600, message="Minimum is 600 seconds (10 minutes)")])  # Default to 15 minutes

    # SMTP connection
    smtp_server = EncryptedCharField(max_length=255)
    smtp_port = models.PositiveIntegerField()
    smtp_username = EncryptedCharField(max_length=255)
    smtp_password = EncryptedCharField(max_length=255)
    smtp_use_tls = models.BooleanField(default=True)

    def __str__(self):
        return f"IMAP/SMTP: {self.email} @ {self.server}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from email_integrations.rescheduler import reschedule_updated_imap_integration
        reschedule_updated_imap_integration(self)
    
    def delete(self, *args, **kwargs):
        scheduler = get_scheduler('sync')
        job_id = f"imap_fetch_{self.id}"
        job = None
        for j in scheduler.get_jobs():
            if j.id == job_id:
                job = j
                break
        if job:
            scheduler.cancel(job)
        super().delete(*args, **kwargs)