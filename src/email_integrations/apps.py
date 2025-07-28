# email_integrations/apps.py
from django.apps import AppConfig
import threading
from django.conf import settings


class EmailIntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_integrations'

    def ready(self):
        from .scheduler import schedule_imap_jobs
        threading.Thread(target=schedule_imap_jobs, daemon=True).start()
