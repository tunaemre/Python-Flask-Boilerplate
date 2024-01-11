import logging
from http import HTTPStatus
from typing import Any, Union

from flask import Flask, Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from src.api.models.base_response import BaseResponse
from src.domain.base.error.base_error import BaseError

logger = logging.getLogger(__name__)


def handle_message(e: Any) -> str:
    if not e.args:
        return ''
    if isinstance(e.args[0], list):
        return ', '.join(e.args[0])
    return ', '.join([str(a) for a in e.args])


def handle_validation_error_message(error: ValidationError) -> str:
    message = 'One or more validation errors occurred:\n'
    errors = '\n'.join([f'{e.get("loc", ("", ))[0]}: {e.get("msg", "")}' for e in error.errors()])

    return message + errors


def handle_base_error(base_error: BaseError) -> Response:
    # Returned Http Status Code is expected from the exception
    logger.warning('Base Error caught. Message: %s - Code: %s',
                   base_error.message,
                   base_error.error_code,
                   exc_info=True)
    return BaseResponse.create_response(success=False,
                                        message=base_error.message,
                                        code=base_error.error_code,
                                        status_code=base_error.status_code)


def handle_validation_error(validation_error: ValidationError) -> Response:
    # Validation errors are caused by invalid input, BadRequest should be returned
    message = handle_validation_error_message(validation_error)
    logger.error('Validation Error caught. Message: %s',
                 message,
                 exc_info=True)
    return BaseResponse.create_response(success=False,
                                        message=message,
                                        status_code=HTTPStatus.BAD_REQUEST)


def handle_http_error(http_error: HTTPException) -> Union[Response, HTTPException]:
    return http_error


def handle_exception(exception: Exception) -> Response:
    # Unhandled exceptions should be returned with InternalServerError
    message = handle_message(exception)
    logger.critical('Unhandled Error caught. Message: %s',
                    message,
                    exc_info=True)

    message = 'Something has gone wrong. Please try later.'

    return BaseResponse.create_response(success=False,
                                        message=message,
                                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


class ErrorHandler:
    @staticmethod
    def initialize(app: Flask) -> None:
        app.register_error_handler(BaseError, handle_base_error)
        app.register_error_handler(ValidationError, handle_validation_error)
        app.register_error_handler(HTTPException, handle_http_error)  # Fallback to default behaviour
        app.register_error_handler(Exception, handle_exception)
