from src.task.mail.mail_worker_service import MailWorkerService
from src.task.task_lock import TaskLock
from src.worker import celery


@celery.task()
def send_expired_mail(name: str, email: str) -> None:
    MailWorkerService.send_expired_mail(name, email)
