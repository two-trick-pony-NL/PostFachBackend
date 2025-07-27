from django.apps import AppConfig
from datetime import timedelta
import django_rq
from django.utils.timezone import now

class EmailIntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_integrations'

    def ready(self):
        print(f"[{now()}] EmailIntegrationsConfig.ready() starting...")

        from email_integrations.models import ImapIntegration
        from email_integrations.tasks import fetch_and_process_imap_emails

        scheduler = django_rq.get_scheduler('default')

        integrations = ImapIntegration.objects.all()
        print(f"[{now()}] Found {integrations.count()} IMAP integrations")

        for integration in integrations:
            job_id = f"imap_fetch_{integration.id}"
            jobs = scheduler.get_jobs()
            if not any(job.id == job_id for job in jobs):
                print(f"[{now()}] Scheduling job for {integration.email} ({integration.id})")
                scheduler.schedule(
                    scheduled_time=now(),
                    func=fetch_and_process_imap_emails,
                    args=[str(integration.id)],
                    interval=30,
                    repeat=None,
                    result_ttl=3600,
                    id=job_id
                )
            else:
                print(f"[{now()}] Job already exists for {integration.email} ({integration.id})")
