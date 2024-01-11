from src.task.status.tasks import update_expired_todos
from src.worker import celery


@celery.task()
def beat_check_expired_todos() -> None:
    update_expired_todos.delay()
