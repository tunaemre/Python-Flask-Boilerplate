from typing import Callable, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from src.config import app_config_manager
from src.domain.common.error.configuration_error import ConfigurationError
from src.domain.todo_list.entity.todo_list_status import TodoListStatuses, TodoListStatus
from src.infrastructure.repository.base.base_repository import BaseRepository, RedisRepository
from src.domain.todo_list.entity.todo_list import TodoList as DomainTodoList
from src.infrastructure.entity.todo_list.todo_list import TodoList


class TodoListRepository(BaseRepository[DomainTodoList],
                         RedisRepository):
    __todo_lists_prefix: Optional[str] = None

    def __init__(self, session_callable: Callable[..., Session]) -> None:
        config = app_config_manager.get_config()
        self.__todo_lists_prefix = config.REDIS_TODO_LISTS_PREFIX
        super().__init__(TodoList, session_callable)

    def get_user_todo_list_key(self, user_id: str) -> str:
        if not self.__todo_lists_prefix:
            raise ConfigurationError('Cannot create todo list key', 'invalid_todo_lists_prefix')
        return f'{self.__todo_lists_prefix}:{user_id}'

    def user_list_todo_lists(self, user_id: str) -> List[DomainTodoList]:

        if todo_lists_redis := self._user_get_todo_lists_from_redis(user_id):
            return todo_lists_redis

        todo_lists = self.query.filter(TodoList.user_id == user_id,
                                       TodoList.status_id != TodoListStatuses.deleted.id).all()

        for todo_list in todo_lists:
            self.add_todo_list_to_redis_entry(DomainTodoList.from_orm(todo_list))

        return [DomainTodoList.from_orm(instance) for instance in todo_lists]

    def user_get_todo_list(self, user_id: str, todo_list_id: str) -> Optional[DomainTodoList]:
        todo_list = self.query.filter(TodoList.id == todo_list_id, TodoList.user_id == user_id,
                                      TodoList.status_id != TodoListStatuses.deleted.id).one_or_none()
        if todo_list:
            todo_list_domain = DomainTodoList.from_orm(todo_list)
            return todo_list_domain
        return None

    def user_get_todo_list_with_todo(self, user_id: str, todo_list_id: str) -> Optional[DomainTodoList]:
        todo_list = self.query.filter(TodoList.id == todo_list_id, TodoList.user_id == user_id,
                                      TodoList.status_id != TodoListStatuses.deleted.id)\
            .options(joinedload(TodoList.todos)) \
            .one_or_none()

        if todo_list:
            todo_list_domain = DomainTodoList.from_orm(todo_list)
            return todo_list_domain
        return None

    def user_update_status(self, user_id: str, todo_list_id: str, status: TodoListStatus) -> bool:
        todo_list = self.query.filter(
            TodoList.id == todo_list_id,
            TodoList.user_id == user_id,
            TodoList.status_id != status.id).one_or_none()

        if todo_list:
            todo_list_domain = DomainTodoList.from_orm(todo_list)
            todo_list_domain.status_id = status.id

            self.update(todo_list_domain)
            return True
        return False

    def _user_get_todo_lists_from_redis(self, user_id: str) -> Optional[List[DomainTodoList]]:
        todo_lists_key = self.get_user_todo_list_key(user_id)
        if todo_lists := self.redis.smembers(todo_lists_key):
            return [DomainTodoList.parse_raw(todo_list) for todo_list in todo_lists]
        return None

    def add_todo_list_to_redis_entry(self, todo_list: DomainTodoList) -> None:
        todo_lists_key = self.get_user_todo_list_key(todo_list.user_id)
        self.redis.sadd(todo_lists_key, todo_list.json())

    def invalidate_redis_entry(self, user_id: str) -> None:
        todo_lists_key = self.get_user_todo_list_key(user_id)
        self.redis.delete(todo_lists_key)
