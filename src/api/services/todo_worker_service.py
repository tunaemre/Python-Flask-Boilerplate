from typing import Optional, List, Tuple

from src.api.services.base.base_service import BaseService
from src.domain.todo.entity.todo import Todo
from src.domain.user.entity.user import User
from src.infrastructure.repository.base.unit_of_work import UnitOfWork


class TodoWorkerService(BaseService):

    def __init__(self, uow: Optional[UnitOfWork] = None) -> None:
        super().__init__(uow)

    def update_expired_todos(self) -> List[Tuple[Todo, User]]:
        """
        Update expired objects.

        :return: Objects and owner users list
        """
        with self.uow:
            todo_user_list = self.uow.todos.worker_update_expired_todos()
        return todo_user_list
