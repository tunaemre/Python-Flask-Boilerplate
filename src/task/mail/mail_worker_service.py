from src.infrastructure.manager.mail_sender_manager import MailSenderManager


class MailWorkerService:

    @staticmethod
    def send_expired_mail(name: str, email: str) -> None:
        # Create an email body
        MailSenderManager.send_mail(recipient=email, name=name)
