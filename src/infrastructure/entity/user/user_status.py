from dataclasses import dataclass

from src.infrastructure.entity.base.base_enum import BaseEnum


@dataclass(init=True)
class UserStatus(BaseEnum):

    @classmethod
    def table_name(cls) -> str:
        return 'user_status'
