from typing import Optional

from src.infrastructure.repository.base.unit_of_work import UnitOfWork


class UOWManager:
    _uow: Optional[UnitOfWork] = None

    @classmethod
    def get_uow(cls) -> UnitOfWork:
        if cls._uow is None:
            cls._uow = UnitOfWork()
        return cls._uow
