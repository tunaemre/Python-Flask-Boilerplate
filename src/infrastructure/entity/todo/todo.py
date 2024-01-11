from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey

from src.domain.base.model.base_entity_model import EType
from src.domain.todo.entity.todo import Todo as DomainTodo
from src.infrastructure.entity.base.base_entity import BaseEntity
from src.infrastructure.entity.todo.todo_status import TodoStatus
from src.infrastructure.entity.todo_list.todo_list import TodoList
from src.infrastructure.entity.user.user import User


@dataclass(init=True)
class Todo(BaseEntity):
    title = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    valid_until = Column(DateTime, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey(User.id), nullable=False)
    todo_list_id = Column(String(36), ForeignKey(TodoList.id), nullable=False)
    status_id = Column(Integer, ForeignKey(TodoStatus.id), nullable=False)

    @classmethod
    def domain_model(cls: Type[Todo]) -> Type[EType]:
        return DomainTodo  # type: ignore
