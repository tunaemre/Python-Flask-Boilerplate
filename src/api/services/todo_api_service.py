from typing import Optional, List
from flask import g
from src.api.models.dto.todo.create_todo_request_dto import CreateTodoRequestDto
from src.api.models.dto.todo.update_todo_request_dto import UpdateTodoRequestDto
from src.api.services.base.base_service import BaseService

from src.domain.todo.entity.todo import Todo
from src.domain.todo.entity.todo_status import TodoStatuses
from src.domain.todo.errors.todo_errors import InvalidTodoError
from src.domain.user.errors.user_errors import UserNotFoundError
import logging
from src.infrastructure.repository.base.unit_of_work import UnitOfWork


class TodoApiService(BaseService):
    logger = logging.getLogger(__name__)

    def __init__(self, uow: Optional[UnitOfWork] = None) -> None:
        super().__init__(uow)

    def get_todo(self, todo_id: str) -> Todo:
        """
        Return object belongs to user.

        :param todo_id: ID of object
        :return: Object of given id
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo = self.uow.todos.user_get_todo(user_id=user.id, todo_id=todo_id)
        if not todo:
            raise InvalidTodoError(todo_id=todo_id)

        return todo

    def get_all_todos(self) -> List[Todo]:
        """
        Return all objects belongs to user.

        :return: Objects of user
        """

        user = g.get('user')
        if not user:
            raise UserNotFoundError

        return self.uow.todos.user_list_todos(user_id=user.id)

    def create_todo(self, todo_request_dto: CreateTodoRequestDto) -> Todo:
        """
        Create a new object for user.

        :param todo_request_dto: Request model to create new object

        :return: Created object instance
        """

        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo = Todo.create(
            todo_request_dto.title,
            todo_request_dto.description,
            todo_request_dto.valid_until,
            user.id,
            todo_request_dto.todo_list_id
        )

        with self.uow:
            self.uow.todos.insert(todo)

        return todo

    def update_todo(self, todo_id: str, todo_request_dto: UpdateTodoRequestDto) -> Todo:
        """
        Update an existing object

        :param todo_id: ID of object
        :param todo_request_dto: Request model to update object
        :return: Updated object instance
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        todo = self.uow.todos.user_get_todo(user_id=user.id, todo_id=todo_id)
        if not todo:
            raise InvalidTodoError(todo_id=todo_id)

        todo.title = todo_request_dto.title
        todo.description = todo_request_dto.description
        todo.valid_until = todo_request_dto.valid_until
        todo.todo_list_id = todo_request_dto.todo_list_id
        todo.status_id = todo_request_dto.status_id

        with self.uow:
            self.uow.todos.update(todo)
        return todo

    def delete_todo(self, todo_id: str) -> None:
        """
        Soft delete an existing object

        :param todo_id: ID of object
        """
        user = g.get('user')
        if not user:
            raise UserNotFoundError

        with self.uow:
            is_updated = self.uow.todos.user_update_status(
                user_id=user.id, todo_id=todo_id, status=TodoStatuses.deleted)
            if not is_updated:
                raise InvalidTodoError(todo_id=todo_id)

    @classmethod
    def on_todo_committed(cls, todo: Todo) -> None:
        """
        A hook for _todo model commit to update can generate parameter of company info with given todo

        :param todo: Todo instance that committed
        :param is_delete: is delete operation
        """
        try:
            service = cls()
            service.update_redis_entry(todo)
        except:
            cls.logger.error(f'ToDo for {todo.id} is not updated at Redis', exc_info=True)

    def update_redis_entry(self, todo: Todo) -> None:
        self.uow.todos.update_todo_redis_entry(todo)
