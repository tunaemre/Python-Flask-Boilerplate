import logging
from http import HTTPStatus
from typing import Any


class BaseError(Exception):
    def __init__(self,
                 message: str,
                 error_code: str,
                 status_code: int = HTTPStatus.BAD_REQUEST,
                 log_level: int = logging.ERROR,
                 **context_data: Any):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.log_level = log_level
        self.context_data = context_data
        super().__init__(message)
