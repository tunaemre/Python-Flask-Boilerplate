from __future__ import annotations

from pydantic import Field

from src.domain.base.model.base_entity_model import BaseEntityModel
from src.domain.user.entity.user_status import UserStatuses, UserStatus


class User(BaseEntityModel):
    sub_id: str = Field(max_length=50)
    email: str = Field(max_length=320)
    status_id: int

    @property
    def status(self) -> UserStatus:
        return UserStatuses.get_status(self.status_id)

    @classmethod
    def create(
            cls,
            sub_id: str,
            email: str
    ) -> User:
        return cls(
            sub_id=sub_id,
            email=email,
            status_id=UserStatuses.enabled.id
        )
