from azure.communication.email import EmailClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging

load_dotenv()

class Settings(BaseSettings):
    acs_connection_string: str
    acs_sender_address: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

class ACSEmailService:
    def __init__(self):
        if not settings.acs_connection_string or not settings.acs_sender_address:
            raise ValueError("ACS_CONNECTION_STRING and ACS_SENDER_ADDRESS must be set.")
        self.client = EmailClient.from_connection_string(settings.acs_connection_string)
        self.sender = settings.acs_sender_address
        logging.basicConfig(level=logging.INFO)

    def send_email(self, recipient_email: str, subject: str, html_content: str):
        if not recipient_email or "@" not in recipient_email:
            logging.error(f"Invalid recipient email: {recipient_email}")
            return {"status": "error", "message": "Invalid recipient email"}

        message = {
            "senderAddress": self.sender,  # ✅ Correct property
            "content": {
                "subject": subject,
                "html": html_content
            },
            "recipients": {
                "to": [{"address": recipient_email}]
            }
        }

        try:
            logging.info(f"Sending email to: {recipient_email}")
            poller = self.client.begin_send(message)
            result = poller.result()
            logging.info(f"Email sent successfully. Operation ID: {result['id']}")
            return {"status": "success", "operation_id": result['id']}
        except Exception as ex:
            logging.error(f"Error sending email: {ex}")
            if hasattr(ex, "response") and ex.response is not None:
                logging.error(f"Azure response: {ex.response.text}")
            return {"status": "error", "message": str(ex)}


# Example usage:
if __name__ == "__main__":
    service = ACSEmailService()
    response = service.send_email(
        recipient_email="sirmanwarsandesh@gmail.com",
        subject="This is to apologize..",
        html_content="<h1>Hii from Hiral.. I'm Sorry for not connecting with you earlier.</h1>"
    )
    print(response)
