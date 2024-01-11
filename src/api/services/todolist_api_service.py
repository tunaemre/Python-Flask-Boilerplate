from typing import Optional, List
from flask import g

from src.api.models.dto.todo_list.create_todo_list_request_dto import CreateTodoListRequestDto
from src.api.models.dto.todo_list.todo_list_with_todos_response_dto import TodoListWithTodosResponseDto
from src.api.models.dto.todo_list.update_todo_list_request_dto import UpdateTodoListRequestDto
from src.api.services.base.base_service import BaseService

from src.domain.todo_list.entity.todo_list import TodoList
import logging

from src.domain.todo_list.entity.todo_list_status import TodoListStatuses
from src.domain.todo_list.errors.todo_list_errors import InvalidTodoListError
from src.domain.user.errors.user_errors import UserNotFoundError
from src.infrastructure.repository.base.unit_of_work import UnitOfWork


class TodoListApiService(BaseService):
    logger = logging.getLogger(__name__)

    def __init__(self, uow: Optional[UnitOfWork] = None) -> None:
        super().__init__(uow)

    def get_todo_lists(self) -> List[TodoList]:
        """
        Return all object belongs to user.
        :return: Objects of user
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        return self.uow.todo_lists.user_list_todo_lists(user_id=user.id)

    def create_todo_list(self, todo_list_request_dto: CreateTodoListRequestDto) -> TodoList:
        """
        Create a new object for user.

        :param todo_list_request_dto: Request model to create new object

        :return: Created object instance
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo_list = TodoList.create(
            todo_list_request_dto.name,
            user.id
        )

        with self.uow:
            self.uow.todo_lists.insert(todo_list)

        return todo_list

    def get_todo_list_with_todos(self, todo_list_id: str) -> TodoList:
        """
        Get the existing object

        :param todo_list_id: ID of object
        :return: Returns object instance
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo_list = self.uow.todo_lists.user_get_todo_list_with_todo(user_id=user.id, todo_list_id=todo_list_id)
        if not todo_list:
            raise InvalidTodoListError(todo_list_id=todo_list_id)

        return todo_list

    def update_todo_list(self, todo_list_id: str, todo_list_request_dto: UpdateTodoListRequestDto) -> TodoList:
        """
        Update an existing object

        :param todo_list_id: ID of object
        :param todo_list_request_dto: Request model to update object
        :return: Updated object instance
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo_list = self.uow.todo_lists.user_get_todo_list(user_id=user.id, todo_list_id=todo_list_id)
        if not todo_list:
            raise InvalidTodoListError(todo_list_id=todo_list_id)

        todo_list.name = todo_list_request_dto.name
        todo_list.status_id = todo_list_request_dto.status_id

        with self.uow:
            self.uow.todo_lists.update(todo_list)
        return todo_list

    def delete_todo_list(self, todo_list_id: str) -> None:
        """
        Soft delete an existing object

        :param todo_list_id: ID of object
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        with self.uow:
            is_updated = self.uow.todo_lists.user_update_status(
                user_id=user.id, todo_list_id=todo_list_id, status=TodoListStatuses.deleted)
            if not is_updated:
                raise InvalidTodoListError(todo_list_id=todo_list_id)

    @classmethod
    def on_todo_list_committed(cls, todo_list: TodoList) -> None:
        """
        A hook for todo_list model commit to update can generate parameter of company info with given todo_list

        :param todo_list: TodoList instance that committed
        """
        try:
            service = cls()
            service.invalidate_redis_entry(todo_list.user_id)
        except:
            cls.logger.error(f'TodoList for {todo_list.id} is not updated at Redis', exc_info=True)

    @classmethod
    def on_todo_committed(cls, user_id: str) -> None:
        """
        A hook for todo_list model commit to update can generate parameter of company info with given todo_list

        :param user_id: user id that committed for
        """
        try:
            service = cls()
            service.invalidate_redis_entry(user_id)
        except:
            cls.logger.error(f'TodoList for {user_id} is not updated at Redis', exc_info=True)

    def add_todo_list_to_redis_entry(self, todo_list: TodoList) -> None:
        self.uow.todo_lists.add_todo_list_to_redis_entry(todo_list)

    def invalidate_redis_entry(self, user_id: str) -> None:
        self.uow.todo_lists.invalidate_redis_entry(user_id)
