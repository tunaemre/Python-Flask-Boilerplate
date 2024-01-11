from typing import Optional

from src.infrastructure.manager.uow_manager import UOWManager
from src.infrastructure.repository.base.unit_of_work import UnitOfWork


class BaseService:

    def __init__(self, uow: Optional[UnitOfWork] = None) -> None:
        self._uow: Optional[UnitOfWork] = uow

    @property
    def uow(self) -> UnitOfWork:
        return UOWManager().get_uow()
