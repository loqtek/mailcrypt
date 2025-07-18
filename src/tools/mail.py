import imapclient
import pyzmail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MailClient:
    def __init__(self, email_address, password, imap_server, smtp_server, imap_port=993, smtp_port=587):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.imap_port = imap_port
        self.smtp_port = smtp_port

    def fetch_emails(self, folder='INBOX', search_criteria='ALL', limit=10):
        """Fetch emails from a specific folder using IMAP."""
        with imapclient.IMAPClient(self.imap_server, ssl=True, port=self.imap_port) as client:
            client.login(self.email_address, self.password)
            client.select_folder(folder)

            uids = client.search(search_criteria)
            uids = sorted(uids, reverse=True)[:limit]

            messages = client.fetch(uids, ['BODY[]', 'FLAGS'])

            result = []

            for uid, msg_data in messages.items():
                msg = pyzmail.PyzMessage.factory(msg_data[b'BODY[]'])
                subject = msg.get_subject()
                from_ = msg.get_addresses('from')
                text = msg.text_part.get_payload().decode(msg.text_part.charset) if msg.text_part else None
                html = msg.html_part.get_payload().decode(msg.html_part.charset) if msg.html_part else None

                result.append({
                    'uid': uid,
                    'subject': subject,
                    'from': from_,
                    'text': text,
                    'html': html
                })

            return result

    def send_email(self, to_addresses, subject, body, is_html=False):
        """Send an email using SMTP."""
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = self.email_address
        msg['To'] = ', '.join(to_addresses)

        if is_html:
            part = MIMEText(body, 'html')
        else:
            part = MIMEText(body, 'plain')

        msg.attach(part)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, to_addresses, msg.as_string())

        return True
