from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.domain.base.model.base_entity_model import EType
from src.infrastructure.entity.base.base_entity import BaseEntity
from src.infrastructure.entity.todo_list.todo_list_status import TodoListStatus
from src.infrastructure.entity.user.user import User
from src.domain.todo_list.entity.todo_list import TodoList as DomainTodoList


@dataclass(init=True)
class TodoList(BaseEntity):
    name = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey(User.id), nullable=False)
    status_id = Column(Integer, ForeignKey(TodoListStatus.id), nullable=False)

    todos = relationship("Todo", lazy="noload")

    @classmethod
    def domain_model(cls: Type[TodoList]) -> Type[EType]:
        return DomainTodoList  # type: ignore
