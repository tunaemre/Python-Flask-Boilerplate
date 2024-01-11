import logging
from http import HTTPStatus
from typing import Any

from src.domain.base.error.base_error import BaseError


class UserNotFoundError(BaseError):
    code = 'user_not_found_error'

    def __init__(self, **context_data: Any) -> None:
        message = 'User not found.'
        super().__init__(message, self.code, log_level=logging.WARNING, status_code=HTTPStatus.UNAUTHORIZED,
                         **context_data)


class DeactivatedUserError(BaseError):
    code = 'deactivated_user'

    def __init__(self, **context_data: Any) -> None:
        message = 'Deactivated user.'
        super().__init__(message, self.code, log_level=logging.WARNING, status_code=HTTPStatus.UNAUTHORIZED,
                         **context_data)
