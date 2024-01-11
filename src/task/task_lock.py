import logging
from datetime import datetime, timedelta
from celery import current_app

from typing import Any


class TaskLock(current_app.Task):
    """
    Celery task base implementation to avoid concurrent task execution by task values
    """

    abstract = True
    default_ttl = 10 * 60  # 10 minutes

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(TaskLock, self).__init__(*args, **kwargs)

    def __generate_lock_cache_key(self, *args: Any, **kwargs: Any) -> str:
        args_key = [str(arg) for arg in args]
        kwargs_key = ['{}:{}'.format(k, str(v)) for k, v in sorted(kwargs.items())]
        return '_'.join([self.name] + args_key + kwargs_key)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        lock_key = f'lock_task:{self.__generate_lock_cache_key(*args, **kwargs)}'
        from src.infrastructure.manager.redis_manager import RedisManager
        redis_instance = RedisManager.get_redis()
        locked = redis_instance.set(
            name=lock_key,
            value=datetime.now().isoformat(),
            ex=timedelta(minutes=self.default_ttl),
            nx=True)

        if locked:
            try:
                return self.run(*args, **kwargs)
            finally:
                redis_instance.delete(lock_key)
        else:
            logging.info(f'Task {self.name} could not be started, '
                         f'because there is another worker which does the same task.')
