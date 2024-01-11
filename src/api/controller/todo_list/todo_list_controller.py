from typing import List

from flask_restx import Namespace, Resource
from flask import Response, request
from http import HTTPStatus

from src.api.controller import ROOT_PATH
from src.api.models.base_response import BaseResponse
from src.api.models.dto.todo_list.create_todo_list_request_dto import CreateTodoListRequestDto
from src.api.models.dto.todo_list.todo_list_with_todos_response_dto import TodoListWithTodosResponseDto
from src.api.models.dto.todo_list.update_todo_list_request_dto import UpdateTodoListRequestDto

from src.api.security.guards import authorization_guard, todo_scope
from src.api.services.todolist_api_service import TodoListApiService
from src.domain.todo_list.entity.todo_list import TodoList

namespace = Namespace(
    'Todo List API',
    description='API for todo list',
    path='/todo_list')

# request dto
create_todo_list_request_schema = namespace.schema_model(
    'create_todo_list_request_schema', CreateTodoListRequestDto.schema())

update_todo_list_request_schema = namespace.schema_model(
    'update_todo_list_request_schema', UpdateTodoListRequestDto.schema())

# response dto
todo_list_response_schema = namespace.schema_model(
    'todo_list_response_schema', BaseResponse[TodoList].schema())

todo_lists_response_schema = namespace.schema_model(
    'todo_lists_response_schema', BaseResponse[List[TodoList]].schema())

todo_list_with_todos_response_schema = namespace.schema_model(
    'todo_list_with_todos_response_schema', BaseResponse[TodoListWithTodosResponseDto].schema())


@namespace.route(ROOT_PATH)
class TodoListController(Resource):
    @namespace.doc(description='Return all todo lists', security='api_key')
    @namespace.response(200, 'OK', todo_lists_response_schema)
    @authorization_guard(todo_scope.read)
    def get(self) -> Response:
        service = TodoListApiService()
        todo_lists = service.get_todo_lists()

        message = 'Todolist obtained.' if todo_lists else \
            'No todolist found.'
        return BaseResponse.create_response(message=message, data=todo_lists)

    @namespace.doc(description='Create a new todo list', security='api_key')
    @namespace.response(200, 'OK', todo_list_response_schema)
    @namespace.expect(create_todo_list_request_schema)
    @authorization_guard(todo_scope.write)
    def post(self) -> Response:
        data = request.get_json()
        todo_list_request_dto = CreateTodoListRequestDto.parse_obj(data)

        service = TodoListApiService()
        todo_list = service.create_todo_list(todo_list_request_dto)

        message = 'Todo list has been created.'
        return BaseResponse.create_response(message=message, data=todo_list, status_code=HTTPStatus.CREATED)


@namespace.route('/<todo_list_id>')
class ToDoListDetailController(Resource):
    @namespace.doc(description='Returns the todo list', security='api_key')
    @namespace.response(200, 'OK', todo_list_response_schema)
    @authorization_guard(todo_scope.read)
    def get(self, todo_list_id: str) -> Response:
        service = TodoListApiService()
        todo_list = service.get_todo_list_with_todos(todo_list_id)

        return BaseResponse.create_response(message='Todo list obtained.', data=todo_list)

    @namespace.doc(description='Updates a Todo list.', security='api_key')
    @namespace.response(200, 'OK')
    @namespace.response(400, 'Invalid todo list')
    @namespace.expect(update_todo_list_request_schema)
    @authorization_guard(todo_scope.write)
    def put(self, todo_list_id: str) -> Response:
        data = request.get_json()
        todo_list_request_dto = UpdateTodoListRequestDto.parse_obj(data)

        service = TodoListApiService()
        todo_list = service.update_todo_list(todo_list_id, todo_list_request_dto)

        return BaseResponse.create_response(message='Todo list has been updated.',
                                            data=todo_list)

    @namespace.doc(description='Deletes a todo list', security='api_key')
    @namespace.response(200, 'OK')
    @namespace.response(400, 'Todo list not found')
    @authorization_guard(todo_scope.write)
    def delete(self, todo_list_id: str) -> Response:
        service = TodoListApiService()
        service.delete_todo_list(todo_list_id)

        return BaseResponse.create_response(message='Todo list has been deleted.',
                                            status_code=HTTPStatus.OK)

