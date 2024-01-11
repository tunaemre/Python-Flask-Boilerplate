
from typing import List, Any
from flask_restx import Namespace

from src.api.models.dto.todo.create_todo_request_dto import CreateTodoRequestDto
from src.domain.todo.entity.todo import Todo
from src.domain.todo_list.entity.todo_list import TodoList

ROOT_PATH = ''


# define model schemas here to register them only once. auth_controller registers these schemas.
def create_schemas(api: Namespace) -> List[Any]:
    return [
        # request dtos
        api.schema_model('CreateTodoRequestDto', CreateTodoRequestDto.schema()),

        # response dtos
        api.schema_model('Todo', Todo.schema()),
        api.schema_model('TodoList', TodoList.schema()),
    ]
