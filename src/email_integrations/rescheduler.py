import django_rq
from django.utils.timezone import now
from datetime import timedelta
from .tasks import fetch_and_process_imap_emails
import random

def reschedule_updated_imap_integration(integration):
    scheduler = django_rq.get_scheduler('sync')    
    job_id = f"imap_fetch_{integration.id}"
    try:
        job = scheduler.get_job(job_id)
        if job:
            scheduler.cancel(job)
    except Exception:
        pass

    scheduled_time = now()
    actual_interval = integration.refresh_interval_seconds + random.randint(-20, 20)

    scheduler.schedule(
        scheduled_time=scheduled_time,
        func=fetch_and_process_imap_emails,
        args=[str(integration.id)],
        interval=actual_interval,
        repeat=None,
        result_ttl=3600,
        id=job_id
    )