import logging
from typing import Any

from src.domain.base.error.base_error import BaseError


class InvalidTodoError(BaseError):
    code = 'invalid_todo'

    def __init__(self, **context_data: Any) -> None:
        message = 'Invalid todo.'
        super().__init__(message, self.code, log_level=logging.WARNING, **context_data)
