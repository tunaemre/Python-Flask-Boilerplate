from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from src.domain.base.model.base_entity_model import BaseEntityModel
from src.domain.todo.entity.todo import Todo
from src.domain.todo_list.entity.todo_list_status import TodoListStatuses, TodoListStatus


class TodoList(BaseEntityModel):
    name: str = Field(max_length=50)
    user_id: str
    status_id: int

    todos: Optional[List[Todo]] = []

    @property
    def status(self) -> TodoListStatus:
        return TodoListStatuses.get_status(self.status_id)

    @classmethod
    def create(
            cls,
            name: str,
            user_id: str,
    ) -> TodoList:
        return cls(
            name=name,
            user_id=user_id,
            status_id=TodoListStatuses.open.id
        )
