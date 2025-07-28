# email_integrations/scheduler.py
from email_integrations.models import ImapIntegration
from email_integrations.tasks import fetch_and_process_imap_emails
from django.utils.timezone import now
from datetime import timedelta
import django_rq
import random
import redis

def schedule_imap_jobs():
    scheduler = django_rq.get_scheduler('sync')
    existing_jobs = {job.id for job in scheduler.get_jobs()}
    print(f"IMAP Scheduler booted. Found {len(existing_jobs)} already scheduled integrations. Scheduling {ImapIntegration.objects.count()-len(existing_jobs)} new integrations:")
    for integration in ImapIntegration.objects.iterator():
        job_id = f"imap_fetch_{integration.id}"
        if job_id not in existing_jobs:
            delay_seconds = random.randint(0, 600)
            scheduled_time = now() + timedelta(seconds=delay_seconds)
            actual_interval = integration.refresh_interval_seconds + random.randint(-20, 20)

            print(f"→ Scheduling job to fetch email from {integration.email} every {integration.refresh_interval_seconds} seconds - ({integration.id}) first run in {delay_seconds} seconds")
            scheduler.schedule(
                scheduled_time=scheduled_time,
                func=fetch_and_process_imap_emails,
                args=[str(integration.id)],
                interval=actual_interval,
                repeat=None,
                result_ttl=3600,
                id=job_id
            )


