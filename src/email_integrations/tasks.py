import logging
from rq import get_current_job
from django.db import transaction
import django_rq
from django.utils.timezone import now
from email.header import decode_header
from email.utils import parsedate_to_datetime, getaddresses, parseaddr

from .services.imap_service import ImapService, get_email_bodies
from .models import ImapIntegration
from emails.models import Email, EmailThread, Contact
from .services.smtp_service import SmtpService

logger = logging.getLogger(__name__)


def decode_mime_header(value):
    parts = decode_header(value)
    return ''.join([
        (text.decode(enc or 'utf-8', errors='ignore') if isinstance(text, bytes) else text)
        for text, enc in parts
    ])


def parse_name_email_list(raw_header):
    return [(name.strip(), email_address.strip().lower()) for name, email_address in getaddresses([raw_header or ""])]


def get_or_create_contact(owner, email_address, display_name=None):
    email_address = email_address.lower().strip()
    contact, created = Contact.objects.get_or_create(
        owner=owner,
        email=email_address,
        defaults={"display_name": display_name or ""},
    )

    if not contact.display_name and display_name:
        contact.display_name = display_name
        contact.save(update_fields=["display_name"])

    return contact


def find_thread_for_email(owner, message_id, in_reply_to, subject):
    if in_reply_to:
        try:
            reply_email = Email.objects.get(owner=owner, message_id=in_reply_to)
            if reply_email.thread:
                return reply_email.thread
        except Email.DoesNotExist:
            pass

    thread_qs = EmailThread.objects.filter(owner=owner, subject__iexact=subject)
    return thread_qs.first() if thread_qs.exists() else None


@transaction.atomic
def create_email_with_thread_and_contacts(integration_user, msg, user_email):
    message_id = msg.get("Message-ID", "").strip()
    if not message_id:
        logger.warning("Email missing Message-ID, skipping")
        return None

    if Email.objects.filter(owner=integration_user, message_id=message_id).exists():
        logger.info(f"Duplicate email detected: {message_id}, skipping")
        return None

    subject_raw = msg.get("Subject", "")
    subject = decode_mime_header(subject_raw)

    in_reply_to = msg.get("In-Reply-To", None)

    from_name, from_email = parseaddr(msg.get("From", ""))
    from_email = from_email.lower().strip()

    to_list = parse_name_email_list(msg.get("To", ""))
    cc_list = parse_name_email_list(msg.get("Cc", ""))
    bcc_list = parse_name_email_list(msg.get("Bcc", ""))

    thread = find_thread_for_email(integration_user, message_id, in_reply_to, subject)
    if not thread:
        thread = EmailThread.objects.create(owner=integration_user, subject=subject)

    plain_body, html_body = get_email_bodies(msg)
    received_at = now()
    date_ = msg.get("Date")
    if date_:
        try:
            received_at = parsedate_to_datetime(date_)
        except Exception:
            pass

    email_obj = Email.objects.create(
        owner=integration_user,
        thread=thread,
        from_email=from_email,
        subject=subject,
        received_at=received_at,
        body=plain_body,
        html_body=html_body,
        message_id=message_id,
        in_reply_to=in_reply_to,
        is_read=False,
        is_starred=False,
        status='received',  # Default status for received emails
        direction='IN',  # Incoming email
    )

    # Link sender
    sender_contact = get_or_create_contact(integration_user, from_email, from_name)
    email_obj.from_contact = sender_contact
    email_obj.save(update_fields=["from_contact"])

    # Add recipients
    for name, email_address in to_list:
        if email_address != user_email:
            contact = get_or_create_contact(integration_user, email_address, name)
            email_obj.to_contacts.add(contact)

    for name, email_address in cc_list:
        if email_address != user_email:
            contact = get_or_create_contact(integration_user, email_address, name)
            email_obj.cc_contacts.add(contact)

    for name, email_address in bcc_list:
        if email_address != user_email:
            contact = get_or_create_contact(integration_user, email_address, name)
            email_obj.bcc_contacts.add(contact)

    return email_obj



def fetch_and_process_imap_emails(integration_id):
    job = get_current_job()
    logger.info(f"Starting IMAP fetch for integration {integration_id} in job {job.id if job else 'unknown'}")

    try:
        integration = ImapIntegration.objects.get(pk=integration_id)

        service = ImapService(
            server=integration.server,
            port=integration.port,
            username=integration.username,
            password=integration.password,
            use_ssl=integration.use_ssl,
        )

        service.connect()
        new_emails = service.fetch_unseen_emails()
        logger.info(f"Fetched {len(new_emails)} new emails for integration {integration.email}")

        for msg in new_emails:
            print("Processing email:", msg.get("Subject", "No Subject"))
            try:
                create_email_with_thread_and_contacts(integration.user, msg, integration.email)
            except Exception:
                logger.exception(f"Failed to process one email for integration {integration_id}")

        service.logout()

    except ImapIntegration.DoesNotExist:
        logger.warning(f"Integration {integration_id} not found, removing scheduled job")
        scheduler = django_rq.get_scheduler('sync')
        job_id = f"imap_fetch_{integration_id}"

        job = None
        for j in scheduler.get_jobs():
            if j.id == job_id:
                job = j
                break

        if job:
            scheduler.cancel(job)
            logger.info(f"Removed scheduled job {job_id} due to missing integration")
        else:
            logger.warning(f"No scheduled job {job_id} found to remove")

    except Exception as e:
        logger.exception(f"IMAP fetch failed for integration {integration_id}: {e}")
        raise




def send_email_task(
    integration_id: str,
    from_email: str,
    to_emails: list,
    subject: str,
    body_text: str = None,
    body_html: str = None,
    attachments: list = None,
    from_name: str = None,
    email_id: str = None,  # optional, to update status
):
    job = get_current_job()
    logger.info(f"Starting SMTP send job {job.id if job else 'unknown'} for integration {integration_id}")

    try:
        integration = ImapIntegration.objects.get(pk=integration_id)
    except ImapIntegration.DoesNotExist:
        logger.error(f"SMTP Integration {integration_id} does not exist")
        return

    service = SmtpService(
        server=integration.smtp_server,
        port=integration.smtp_port,
        username=integration.smtp_username,
        password=integration.smtp_password,
        use_tls=integration.smtp_use_tls,
    )

    try:
        service.connect()
        service.send_email(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
            from_name=from_name,
        )
        logger.info(f"Email sent successfully via integration {integration.email}")

        if email_id:
            try:
                email_obj = Email.objects.get(id=email_id)
                email_obj.status = 'sent'
                email_obj.save(update_fields=['status'])
            except Email.DoesNotExist:
                logger.warning(f"Email with id {email_id} not found to update status")
    except Exception:
        logger.exception("Failed to send email")
        if email_id:
            try:
                email_obj = Email.objects.get(id=email_id)
                email_obj.status = 'failed'
                email_obj.save(update_fields=['status'])
            except Email.DoesNotExist:
                pass
        raise
    finally:
        service.disconnect()