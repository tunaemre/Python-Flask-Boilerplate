from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.domain.common.validator.datetime import check_valid_until


class UpdateTodoRequestDto(BaseModel):
    title: str = Field(max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    valid_until: datetime
    todo_list_id: str
    status_id: int

    # validators
    _check_valid_until: classmethod = validator('valid_until', allow_reuse=True)(check_valid_until)  # type: ignore
