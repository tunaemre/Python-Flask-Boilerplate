from typing import Optional, Any

from src.infrastructure.client.mail_sender_client import MailSenderClient


class MailSenderManager:
    __mail_sender_client: Optional[MailSenderClient] = None

    @classmethod
    def get_mail_sender_client(cls) -> MailSenderClient:
        if cls.__mail_sender_client is None:
            cls.__mail_sender_client = MailSenderClient()
        return cls.__mail_sender_client

    @classmethod
    def send_mail(cls, recipient: str, **email_data: Any) -> None:
        mail_sender_client = cls.get_mail_sender_client()
        mail_sender_client.send_mail(recipient=recipient, **email_data)
