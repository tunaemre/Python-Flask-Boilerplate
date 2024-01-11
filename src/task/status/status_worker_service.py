from typing import List, Any, Tuple, Optional

from src.domain.todo.entity.todo import Todo
from src.domain.user.entity.user import User
from src.infrastructure.client.todo_api_client import TodoApiClient

todo_api_client = TodoApiClient()


class StatusWorkerService:

    @staticmethod
    def update_expired_todos() -> Optional[List[Tuple[Todo, User]]]:
        return todo_api_client.update_expired_todos()
