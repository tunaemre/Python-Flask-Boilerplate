from typing import List
from http import HTTPStatus

from flask_restx import Resource, Namespace
from flask import Response, request

from src.api.controller import create_schemas, ROOT_PATH
from src.api.models.base_response import BaseResponse
from src.api.models.dto.todo.create_todo_request_dto import CreateTodoRequestDto
from src.api.models.dto.todo.update_todo_request_dto import UpdateTodoRequestDto
from src.api.security.guards import authorization_guard, todo_scope
from src.api.services.todo_api_service import TodoApiService
from src.domain.todo.entity.todo import Todo

namespace = Namespace(
    'Todo API',
    description='API for todos',
    path='/todo')

used_schemas = create_schemas(namespace)

# request dto
create_todo_request_schema = namespace.schema_model(
    'create_todo_request_schema', CreateTodoRequestDto.schema())


update_todo_request_schema = namespace.schema_model(
    'update_todo_request_schema', UpdateTodoRequestDto.schema())

# response dto
todo_response_schema = namespace.schema_model(
    'todo_response_schema', BaseResponse[Todo].schema())

todo_list_response_schema = namespace.schema_model(
    'todo_response_schema', BaseResponse[List[Todo]].schema())


@namespace.route(ROOT_PATH)
class ToDoController(Resource):
    @namespace.doc(description='Returns all todos', security='api_key')
    @namespace.response(200, 'OK', todo_list_response_schema)
    @authorization_guard(todo_scope.read)
    def get(self) -> Response:
        todo_api = TodoApiService()
        todos = todo_api.get_all_todos()

        message = 'Todo obtained.' if todos else \
            'No todo found.'
        return BaseResponse.create_response(message=message, data=todos)

    @namespace.doc(description='Create a new todo ', security='api_key')
    @namespace.response(201, 'Created', todo_response_schema)
    @namespace.expect(*used_schemas, create_todo_request_schema)
    @authorization_guard(todo_scope.write)
    def post(self) -> Response:
        data = request.get_json()
        todo_request_dto = CreateTodoRequestDto.parse_obj(data)

        todo_api = TodoApiService()
        todo = todo_api.create_todo(todo_request_dto)

        message = 'Todo has been created.'
        return BaseResponse.create_response(message=message, data=todo, status_code=HTTPStatus.CREATED)


@namespace.route('/<todo_id>')
class ToDoDetailController(Resource):
    @namespace.doc(description='Returns the todo', security='api_key')
    @namespace.response(200, 'OK', todo_response_schema)
    @authorization_guard(todo_scope.read)
    def get(self, todo_id: str) -> Response:
        todo_api = TodoApiService()
        todo = todo_api.get_todo(todo_id)

        return BaseResponse.create_response(message='Todo obtained.', data=todo)

    @namespace.doc(description='Updates a Todo.', security='api_key')
    @namespace.response(200, 'OK')
    @namespace.response(400, 'Invalid todo')
    @namespace.expect(update_todo_request_schema)
    @authorization_guard(todo_scope.write)
    def put(self, todo_id: str) -> Response:
        data = request.get_json()
        todo_request_dto = UpdateTodoRequestDto.parse_obj(data)

        todo_api = TodoApiService()
        todo = todo_api.update_todo(todo_id, todo_request_dto)

        return BaseResponse.create_response(message='Todo has been updated.',
                                            data=todo)

    @namespace.doc(description='Deletes a todo', security='api_key')
    @namespace.response(200, 'OK')
    @namespace.response(400, 'Todo not found')
    @authorization_guard(todo_scope.write)
    def delete(self, todo_id: str) -> Response:
        todo_api = TodoApiService()
        todo_api.delete_todo(todo_id)

        return BaseResponse.create_response(message='Todo has been deleted.',
                                            status_code=HTTPStatus.OK)
