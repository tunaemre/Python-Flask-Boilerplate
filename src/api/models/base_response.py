from __future__ import annotations

from http import HTTPStatus
from typing import Optional, TypeVar, Generic

from flask import Response
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')


class BaseResponse(GenericModel, Generic[DataT]):
    success: bool = True
    message: Optional[str] = None
    code: Optional[str] = None
    data: Optional[DataT] = None

    @classmethod
    def create_response(cls,
                        success: bool = True,
                        message: Optional[str] = None,
                        code: Optional[str] = None,
                        data: Optional[DataT] = None,
                        status_code: int = HTTPStatus.OK) -> Response:
        base_response = cls(success=success, message=message, code=code, data=data)
        return Response(response=base_response.json(exclude_none=True, ensure_ascii=False), status=status_code,
                        mimetype='application/json; charset=utf-8')
