# Suppose you have the appointment object from DB
from azure.communication.email import EmailClient
from app.core.config import settings  # or wherever your ACS connection string lives

class ACSEmailService:
    def __init__(self):
        self.client = EmailClient.from_connection_string(settings.ACS_CONNECTION_STRING)

    def send_email(self, recipient_email: str, subject: str, html_content: str):
        message = {
            "senderAddress": settings.ACS_SENDER_EMAIL,
            "recipients": {"to": [{"address": recipient_email}]},
            "content": {"subject": subject, "html": html_content}
        }
        response = self.client.begin_send(message).result()
        return response