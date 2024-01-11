from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from src.domain.base.model.base_entity_model import BaseEntityModel
from src.domain.todo.entity.todo_status import TodoStatus, TodoStatuses


class Todo(BaseEntityModel):
    title: str = Field(max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    valid_until: datetime
    user_id: str
    todo_list_id: str
    status_id: int

    @property
    def status(self) -> TodoStatus:
        return TodoStatuses.get_status(self.status_id)

    @classmethod
    def create(
            cls,
            title: str,
            description: Optional[str],
            valid_until: datetime,
            user_id: str,
            todo_list_id: str
    ) -> Todo:
        return cls(
            title=title,
            description=description,
            valid_until=valid_until,
            user_id=user_id,
            todo_list_id=todo_list_id,
            status_id=TodoStatuses.open.id
        )
