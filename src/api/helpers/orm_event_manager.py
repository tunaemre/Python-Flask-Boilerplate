from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper

from src.api.services.todo_api_service import TodoApiService
from src.api.services.todolist_api_service import TodoListApiService
from src.infrastructure.entity.todo.todo import Todo
from src.domain.todo.entity.todo import Todo as DomainTodo
from src.infrastructure.entity.todo_list.todo_list import TodoList
from src.domain.todo_list.entity.todo_list import TodoList as DomainTodoList


class OrmEventManager:

    @staticmethod
    def init() -> None:

        @event.listens_for(Todo, 'after_insert')
        def receive_after_insert(mapper: Mapper, connection: Connection, target: Todo) -> None:
            OrmEventManager._on_todo_committed(target)

        @event.listens_for(Todo, 'after_update')
        def receive_after_update(mapper: Mapper, connection: Connection, target: Todo) -> None:
            OrmEventManager._on_todo_committed(target)

        @event.listens_for(TodoList, 'after_insert')  # type: ignore
        def receive_after_insert(mapper: Mapper, connection: Connection, target: TodoList) -> None:
            OrmEventManager._on_todo_list_committed(target)

        @event.listens_for(TodoList, 'after_update')  # type: ignore
        def receive_after_update(mapper: Mapper, connection: Connection, target: TodoList) -> None:
            OrmEventManager._on_todo_list_committed(target)

    @staticmethod
    def _on_todo_committed(todo: Todo) -> None:
        domain_todo = DomainTodo.parse_obj(todo.__dict__)
        TodoApiService.on_todo_committed(domain_todo)

        # clear todo list cache
        TodoListApiService.on_todo_committed(domain_todo.user_id)

    @staticmethod
    def _on_todo_list_committed(todo_list: TodoList) -> None:
        domain_todo_list = DomainTodoList.parse_obj(todo_list.__dict__)
        TodoListApiService.on_todo_list_committed(domain_todo_list)
