from typing import Any

from src.config import worker_config_manager
from src.domain.common.error.configuration_error import ConfigurationError


class MailSenderClient:

    def __init__(self) -> None:
        config = worker_config_manager.get_config()
        if not config.MAIL_SENDER_API_KEY:
            raise ConfigurationError(
                'MAIL_SENDER_API_KEY must be provided.', 'mail_sender_client_initialization_error')
        self.api_key = config.MAIL_SENDER_API_KEY

    def send_mail(self, recipient: str, **email_data: Any) -> None:
        # Send mail
        pass
