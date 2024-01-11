import logging

from src.task.status.status_worker_service import StatusWorkerService
from src.task.mail.tasks import send_expired_mail
from src.task.task_lock import TaskLock
from src.worker import celery


logger = logging.getLogger(__name__)


@celery.task(base=TaskLock)
def update_expired_todos() -> None:
    todo_user_list = StatusWorkerService.update_expired_todos()
    if not todo_user_list:
        logger.info('No expired todo found.')
        return

    for todo, user in todo_user_list:
        send_expired_mail.delay(todo.title, user.email)


