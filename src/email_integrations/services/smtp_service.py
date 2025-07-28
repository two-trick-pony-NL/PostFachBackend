import smtplib
from email.message import EmailMessage
from email.utils import formataddr

class SmtpService:
    def __init__(self, server, port, username, password, use_tls=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.connection = None

    def connect(self):
        self.connection = smtplib.SMTP(self.server, self.port)
        self.connection.ehlo()
        if self.use_tls:
            self.connection.starttls()
            self.connection.ehlo()
        self.connection.login(self.username, self.password)

    def send_email(self, from_email, to_emails, subject, body_text=None, body_html=None, attachments=None, from_name=None):
        """
        - to_emails: list of recipient emails
        - attachments: list of dicts with keys: filename, content (bytes), mime_type (str)
        """
        msg = EmailMessage()
        if from_name:
            msg['From'] = formataddr((from_name, from_email))
        else:
            msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        if body_html and body_text:
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype='html')
        elif body_html:
            msg.add_alternative(body_html, subtype='html')
        else:
            msg.set_content(body_text or '')

        if attachments:
            for attach in attachments:
                msg.add_attachment(
                    attach['content'],
                    maintype=attach['mime_type'].split('/')[0],
                    subtype=attach['mime_type'].split('/')[1],
                    filename=attach['filename']
                )

        self.connection.send_message(msg)

    def disconnect(self):
        if self.connection:
            self.connection.quit()
            self.connection = None
