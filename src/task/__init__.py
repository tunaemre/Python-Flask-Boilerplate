from typing import Any

from celery.signals import after_setup_logger

from src.infrastructure.logging.log_manager import LogManager
from src.worker import configuration


@after_setup_logger.connect
def celery_after_setup_logger(**kwargs: Any) -> None:
    LogManager.init_logger(configuration)

from src.task import beats  # NOQA
from src.task.status import tasks as status_tasks  # NOQA
from src.task.mail import tasks as mail_tasks  # NOQA
