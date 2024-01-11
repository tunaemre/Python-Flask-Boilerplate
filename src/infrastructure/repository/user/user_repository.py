from typing import Callable, Optional

from sqlalchemy.orm import Session

from src.domain.user.entity.user import User as DomainUser
from src.infrastructure.entity.user.user import User
from src.infrastructure.repository.base.base_repository import BaseRepository


class UserRepository(BaseRepository[DomainUser]):

    def __init__(self, session_callable: Callable[..., Session]) -> None:
        super().__init__(User, session_callable)

    def get_by_email(self, email: str) -> Optional[DomainUser]:
        user = self.query.filter_by(email=email).one_or_none()
        if user:
            return DomainUser.from_orm(user)
        return None

    def get_sub_id(self, sub_id: str) -> Optional[DomainUser]:
        user = self.query.filter_by(sub_id=sub_id).one_or_none()
        if user:
            return DomainUser.from_orm(user)
        return None

