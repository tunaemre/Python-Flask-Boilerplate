from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from sqlalchemy import Column, String, Integer, ForeignKey

from src.domain.base.model.base_entity_model import EType
from src.domain.user.entity.user import User as DomainUser
from src.infrastructure.entity.base.base_entity import BaseEntity
from src.infrastructure.entity.user.user_status import UserStatus


@dataclass(init=True)
class User(BaseEntity):
    sub_id = Column(String(50), index=True, nullable=False)
    email = Column(String(320), index=True, unique=True, nullable=False)
    status_id = Column(Integer, ForeignKey(UserStatus.id), nullable=False)

    @classmethod
    def domain_model(cls: Type[User]) -> Type[EType]:
        return DomainUser  # type: ignore
