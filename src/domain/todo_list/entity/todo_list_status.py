from typing import Dict, List

from src.domain.base.model.base_enum_model import BaseEnumModel


class TodoListStatus(BaseEnumModel):
    name: str


class TodoListStatuses:
    open = TodoListStatus.construct(id=1, name='Open')
    closed = TodoListStatus.construct(id=2, name='Closed')
    deleted = TodoListStatus.construct(id=3, name='Deleted')

    _statuses: Dict[int, TodoListStatus] = {
        1: open,
        2: closed,
        3: deleted
    }

    @classmethod
    def get_status(cls, status_id: int) -> TodoListStatus:
        if status_id in cls._statuses:
            return cls._statuses[status_id]
        raise ValueError(f'Status ID {status_id} does not exist in the predefined todo list status ids.')

    @classmethod
    def get_all(cls) -> List[TodoListStatus]:
        return list(cls._statuses.values())
