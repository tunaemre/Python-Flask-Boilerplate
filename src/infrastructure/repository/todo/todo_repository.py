from datetime import datetime
from typing import List, Callable, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.sql import operators

from src.config import app_config_manager
from src.domain.common.error.configuration_error import ConfigurationError
from src.domain.todo.entity.todo import Todo as DomainTodo
from src.domain.todo.entity.todo_status import TodoStatus, TodoStatuses
from src.domain.user.entity.user import User as DomainUser
from src.infrastructure.entity.todo.todo import Todo
from src.infrastructure.entity.user.user import User
from src.infrastructure.repository.base.base_repository import BaseRepository, RedisRepository


class TodoRepository(BaseRepository[DomainTodo],
                     RedisRepository):

    _inactive_todo_redis_ttl = 5 * 60  # TTL in seconds for todos cache
    __todos_prefix: Optional[str] = None

    def __init__(self, session_callable: Callable[..., Session]) -> None:
        config = app_config_manager.get_config()
        self.__todos_prefix = config.REDIS_TODOS_PREFIX
        super().__init__(Todo, session_callable)

    def get_todo_key(self, todo_id: str) -> str:
        if not self.__todos_prefix:
            raise ConfigurationError('Cannot create todo key', 'invalid_todos_prefix')
        return f'{self.__todos_prefix}:{todo_id}'

    def user_list_todos(self, user_id: str) -> List[DomainTodo]:
        todos = self.query.filter(Todo.user_id == user_id,
                                  Todo.status_id != TodoStatuses.deleted.id).all()
        return [DomainTodo.from_orm(instance) for instance in todos]

    def user_get_todo(self, user_id: str, todo_id: str) -> Optional[DomainTodo]:
        if todo := self._user_get_todo_from_redis(todo_id):
            if todo.status_id == TodoStatuses.deleted.id:
                return None
            return todo

        todo = self.query.filter(Todo.id == todo_id, Todo.user_id == user_id,
                                 Todo.status_id != TodoStatuses.deleted.id).one_or_none()
        if todo:
            todo_domain = DomainTodo.from_orm(todo)
            self.update_todo_redis_entry(todo_domain)
            return todo_domain
        return None

    def _user_get_todo_from_redis(self, todo_id: str) -> Optional[DomainTodo]:
        todo_key = self.get_todo_key(todo_id)
        if todo := self.redis.get(todo_key):
            return DomainTodo.parse_raw(todo)
        return None

    def update_todo_redis_entry(self, todo: DomainTodo) -> None:
        todo_key = self.get_todo_key(todo.id)
        self.redis.set(todo_key, todo.json(), ex=self._inactive_todo_redis_ttl)

    def user_list_todos_by_status(self, user_id: str, status: TodoStatus) -> List[DomainTodo]:
        todos = self.query.filter_by(user_id=user_id, status_id=status.id).all()
        return [DomainTodo.from_orm(instance) for instance in todos]

    def user_update_status(self, user_id: str, todo_id: str, status: TodoStatus) -> bool:
        todo = self.query.filter(
            Todo.id == todo_id,
            Todo.user_id == user_id,
            Todo.status_id != status.id).one_or_none()

        if todo:
            todo_domain = DomainTodo.from_orm(todo)
            todo_domain.status_id = status.id

            self.update(todo_domain)
            return True
        return False

    def worker_update_expired_todos(self) -> List[Tuple[DomainTodo, DomainUser]]:
        id_list = self.session.query(Todo.id).filter(
            Todo.status_id == TodoStatuses.open.id,
            Todo.valid_until < datetime.utcnow()
        ).all()

        id_list = [obj_id for obj_id, in id_list]

        self.query.filter(operators.in_op(Todo.id, id_list),
                          Todo.status_id == TodoStatuses.open.id) \
            .update({Todo.status_id: TodoStatuses.expired.id},
                    synchronize_session=False)

        todo_user_list = self.session.query(Todo, User).join(User, Todo.user_id == User.id)\
            .filter(operators.in_op(Todo.id, id_list),
                    Todo.status_id == TodoStatuses.expired.id).all()

        return [(DomainTodo.from_orm(todo), DomainUser.from_orm(user)) for todo, user in todo_user_list]
