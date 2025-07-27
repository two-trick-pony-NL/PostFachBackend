import uuid
from django.db import models
from email.utils import parseaddr


class UserProfile(models.Model):
    # User ID corresponds to the Supabase user ID
    id = models.UUIDField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_username = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" or str(self.supabase_user_id)

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='contacts')
    email = models.EmailField()
    display_name = models.CharField(max_length=100, blank=True)

    always_notify = models.BooleanField(default=False, help_text="Always notify user for emails from this contact")
    muted = models.BooleanField(default=False, help_text="Mute all emails from this contact")
    marked_as_spam = models.BooleanField(default=False, help_text="Automatically mark emails from this contact as spam")

    important = models.BooleanField(default=False, help_text="Mark this contact as important (priority)")
    whitelist = models.BooleanField(default=False, help_text="Bypass spam filters for this contact")

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.display_name:
            display_name, email_addr = parseaddr(self.email)
            if display_name:
                self.display_name = display_name
        super().save(*args, **kwargs)
        
        
        
        

class DummyModel(models.Model):
    class Meta:
        verbose_name = "RQ Dashboard"
        verbose_name_plural = "RQ Dashboard"
