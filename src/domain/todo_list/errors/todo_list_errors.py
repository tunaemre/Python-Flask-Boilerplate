import logging
from typing import Any

from src.domain.base.error.base_error import BaseError


class InvalidTodoListError(BaseError):
    code = 'invalid_todo_list'

    def __init__(self, **context_data: Any) -> None:
        message = 'Invalid todo list.'
        super().__init__(message, self.code, log_level=logging.WARNING, **context_data)
