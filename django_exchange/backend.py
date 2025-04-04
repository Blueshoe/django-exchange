from email.utils import parseaddr
import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox,FileAttachment


class ExchangeEmailBackend(BaseEmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None, fail_silently=False, domain=None, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER if username is None else username
        self.password = settings.EMAIL_HOST_PASSWORD if password is None else password
        if domain:
            self.domain = domain
        else:
            try:
                self.domain = settings.EMAIL_DOMAIN
            except AttributeError:
                self.domain = None
        self.credentials = None
        self._lock = threading.RLock()

    def open(self):
        """
        Setup credentials to talk to the Exchange server.
        """
        if self.credentials:
            # Nothing to do if the connection is already open.
            return False

        try:
            username_prefix = f'{self.domain}\\' if self.domain else ''
            self.credentials = Credentials(username=f'{username_prefix}{self.username}', password=self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise

    def close(self):
        """Unset credentials.."""
        if self.credentials is None:
            return
        self.credentials = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.credentials or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        # from_email could be a formatted email string, e.g. "FOO <foo@bar.com>"
        _, from_email_address = parseaddr(from_email)

        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        try:
            account = Account(
                primary_smtp_address=from_email_address, credentials=self.credentials, autodiscover=True,
                access_type=DELEGATE
            )
            exchange_message = Message(
                account=account, subject=email_message.subject, body=email_message.body,
                to_recipients=[Mailbox(email_address=recipient) for recipient in recipients]
            )
            # Convert Django attachments to Exchange FileAttachments
            exch_attachments = []
            for attachment in email_message.attachments:
                if isinstance(attachment, tuple) and len(attachment) == 3:
                    filename, content, mimetype = attachment
                    if isinstance(content, str):
                        content = content.encode(encoding)
                    exch_attachments.append(FileAttachment(name=filename, content=content))

            if exch_attachments:
                exchange_message.attachments = exch_attachments
            exchange_message.send()
        except Exception:
            if not self.fail_silently:
                raise
            return False
        return True
