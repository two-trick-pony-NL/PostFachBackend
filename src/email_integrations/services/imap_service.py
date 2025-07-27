import imaplib
import email
from email.header import decode_header
import logging

logger = logging.getLogger(__name__)

class ImapService:
    def __init__(self, server, port, username, password, use_ssl=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None

    def connect(self):
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            self.connection.login(self.username, self.password)
        except Exception as e:
            logger.exception(f"IMAP connect/login failed: {e}")
            self.connection = None
            raise

    def fetch_unseen_emails(self, folder="INBOX"):
        if not self.connection:
            logger.error("No IMAP connection established")
            return []

        try:
            typ, data = self.connection.select(folder)
            if typ != "OK":
                logger.error(f"Failed to select folder {folder}: {typ}")
                return []

            status, messages = self.connection.search(None, '(UNSEEN)')
            if status != "OK":
                logger.error(f"Failed to search unseen emails: {status}")
                return []

            email_ids = messages[0].split()
            emails = []

            for eid in email_ids:
                status, msg_data = self.connection.fetch(eid, "(RFC822)")
                if status != "OK":
                    logger.warning(f"Failed to fetch email id {eid}")
                    continue
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append(msg)

            return emails

        except Exception as e:
            logger.exception(f"Error during fetching emails: {e}")
            return []

    def logout(self):
        try:
            if self.connection:
                self.connection.logout()
        except Exception as e:
            logger.warning(f"Error during IMAP logout: {e}")
        finally:
            self.connection = None


def get_email_bodies(msg):
    plain_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    plain_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    plain_body = ""
            elif content_type == "text/html" and "attachment" not in content_disposition:
                try:
                    html_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    html_body = ""
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            plain_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
        elif content_type == "text/html":
            html_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")

    return plain_body, html_body