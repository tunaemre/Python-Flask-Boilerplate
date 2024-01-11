from typing import Union

from src.api.models.base_response import BaseResponse
from flask import json, Response
from werkzeug.test import TestResponse


def get_api_url(url: str) -> str:
    return f'/api/v1{url}'


def get_base_response(response: Union[Response, TestResponse]) -> BaseResponse:
    response_json = json.loads(response.data)
    return BaseResponse(**response_json)
