from typing import Dict, List

from src.domain.base.model.base_enum_model import BaseEnumModel


class TodoStatus(BaseEnumModel):
    name: str


class TodoStatuses:
    open = TodoStatus.construct(id=1, name='Open')
    closed = TodoStatus.construct(id=2, name='Closed')
    expired = TodoStatus.construct(id=3, name='Expired')
    deleted = TodoStatus.construct(id=4, name='Deleted')

    _statuses: Dict[int, TodoStatus] = {
        1: open,
        2: closed,
        3: expired,
        4: deleted
    }

    @classmethod
    def get_status(cls, status_id: int) -> TodoStatus:
        if status_id in cls._statuses:
            return cls._statuses[status_id]
        raise ValueError(f'Status ID {status_id} does not exist in the predefined todo status ids.')

    @classmethod
    def get_all(cls) -> List[TodoStatus]:
        return list(cls._statuses.values())
