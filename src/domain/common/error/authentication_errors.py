import logging
from http import HTTPStatus
from typing import Any

from src.domain.base.error.base_error import BaseError


class InvalidTokenError(BaseError):
    code = 'invalid_token'

    def __init__(self, **context_data: Any) -> None:
        message = 'Invalid Token.'
        super().__init__(message, self.code, status_code=HTTPStatus.UNAUTHORIZED,
                         log_level=logging.CRITICAL, **context_data)


class PermissionDeniedError(BaseError):
    code = 'permission_denied'

    def __init__(self, **context_data: Any) -> None:
        message = 'Permission Denied.'
        super().__init__(message, self.code, status_code=HTTPStatus.FORBIDDEN,
                         log_level=logging.CRITICAL, **context_data)
