import logging
from rq import get_current_job
from .services.imap_service import ImapService, get_email_bodies
from .models import ImapIntegration
from emails.models import Email, EmailThread, Contact
from django.utils.timezone import now
from email.header import decode_header
from email.utils import parsedate_to_datetime, getaddresses, parseaddr
from django.db import transaction

logger = logging.getLogger(__name__)


def get_or_create_contact(owner, email_address):
    email_address = email_address.lower().strip()
    contact, created = Contact.objects.get_or_create(
        owner=owner,
        email=email_address,
        defaults={"display_name": parseaddr(email_address)[0]},
    )
    return contact


def find_thread_for_email(owner, message_id, in_reply_to, subject):
    if in_reply_to:
        try:
            reply_email = Email.objects.get(owner=owner, message_id=in_reply_to)
            if reply_email.thread:
                return reply_email.thread
        except Email.DoesNotExist:
            pass
    threads = EmailThread.objects.filter(owner=owner, subject__iexact=subject)
    if threads.exists():
        return threads.first()
    return None


@transaction.atomic
def create_email_with_thread_and_contacts(integration_user, msg):
    message_id = msg.get("Message-ID", "").strip()
    if not message_id:
        logger.warning("Email missing Message-ID, skipping")
        return None

    # Avoid duplicates
    if Email.objects.filter(owner=integration_user, message_id=message_id).exists():
        logger.info(f"Duplicate email detected: {message_id}, skipping")
        return None

    subject, encoding = decode_header(msg.get("Subject", ""))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    in_reply_to = msg.get("In-Reply-To", None)
    from_raw = msg.get("From", "")
    to_raw = msg.get("To", "")
    cc_raw = msg.get("Cc", "")
    bcc_raw = msg.get("Bcc", "")

    from_email = parseaddr(from_raw)[1].lower()
    to_emails = [email.lower() for name, email in getaddresses([to_raw])]
    cc_emails = [email.lower() for name, email in getaddresses([cc_raw])]
    bcc_emails = [email.lower() for name, email in getaddresses([bcc_raw])]
    all_recipients = set(to_emails + cc_emails + bcc_emails)

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
        to_emails=", ".join(all_recipients),
        is_read=False,
        is_starred=False,
    )

    sender_contact = get_or_create_contact(integration_user, from_email)
    email_obj.from_contact = sender_contact
    email_obj.save()

    for recipient_email in all_recipients:
        contact = get_or_create_contact(integration_user, recipient_email)
        email_obj.to_contacts.add(contact)

    return email_obj


def fetch_and_process_imap_emails(integration_id):
    job = get_current_job()
    print(f"Starting IMAP fetch for integration {integration_id} in job {job.id if job else 'unknown'}")
    try:
        print("Fetching IMAP integration details...")
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
        print(f"Fetched {len(new_emails)} new emails for integration {integration.email}")

        for msg in new_emails:
            try:
                create_email_with_thread_and_contacts(integration.user, msg)
            except Exception:
                logger.exception(f"Failed to process one email for integration {integration_id}")

        service.logout()

    except Exception as e:
        logger.exception(f"IMAP fetch failed for integration {integration_id}: {e}")
        raise
