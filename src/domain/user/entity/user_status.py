from typing import Dict, List

from src.domain.base.model.base_enum_model import BaseEnumModel


class UserStatus(BaseEnumModel):
    name: str


class UserStatuses:
    enabled = UserStatus.construct(id=1, name='Enabled')
    disabled = UserStatus.construct(id=2, name='Disabled')

    _statuses: Dict[int, UserStatus] = {
        1: enabled,
        2: disabled
    }

    @classmethod
    def get_status(cls, status_id: int) -> UserStatus:
        if status_id in cls._statuses:
            return cls._statuses[status_id]
        raise ValueError(f'Status ID {status_id} does not exist in the predefined user status ids.')

    @classmethod
    def get_all(cls) -> List[UserStatus]:
        return list(cls._statuses.values())
