from typing import List

from pydantic import BaseModel, Field

from src.domain.todo.entity.todo import Todo


class TodoListWithTodosResponseDto(BaseModel):
    name: str = Field(max_length=50)
    user_id: str
    status_id: int
    todos: List[Todo]
