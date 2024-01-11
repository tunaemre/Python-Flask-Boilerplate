import uuid

import pytest

from datetime import datetime, timedelta
from flask.testing import FlaskClient
from http import HTTPStatus

from src.api.security.guards import todo_scope, worker_scope
from src.domain.common.error.authentication_errors import PermissionDeniedError
from src.domain.todo.entity.todo import Todo
from src.domain.todo.entity.todo_status import TodoStatuses
from src.domain.todo_list.entity.todo_list import TodoList
from src.domain.todo_list.entity.todo_list_status import TodoListStatuses
from src.infrastructure.repository.base.unit_of_work import UnitOfWork
from test import test_user_email
from test.e2e import get_api_url, get_base_response
from test.fakes.fake_authenticator import fake_permission


@pytest.mark.usefixtures('client', 'db_session')
class TestTodoController:

    @fake_permission(worker_scope.worker)  # Set token without user permission
    def test_get_all_todos_forbidden(self, client: FlaskClient):
        response = client.get(get_api_url('/todo'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert base_response.code == PermissionDeniedError.code
        assert response.status_code == HTTPStatus.FORBIDDEN

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_all_todos_empty_case(self, client: FlaskClient):
        response = client.get(get_api_url('/todo'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == "No todo found."
        assert base_response.data == []

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_create_todo_dto_error(self, client: FlaskClient):
        response = client.post(
            get_api_url('/todo'),
            json={
                'description': "description",
                'valid_until': (datetime.utcnow() + timedelta(days=7)).date().strftime('%Y-%m-%dT%H:%M:%S%z')
            })

        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_create_todo_valid_until_earlier_than_today(self, client: FlaskClient):
        response = client.post(
            get_api_url('/todo'),
            json={
                'title': 'title',
                'description': "description",
                'valid_until': (datetime.utcnow() - timedelta(days=7)).date().strftime('%Y-%m-%dT%H:%M:%S%z')
            })

        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_create_todo_success(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)

        todo_list = TodoList(
            name="name",
            user_id=user.id,
            status_id=TodoListStatuses.open.id
        )
        uow.todo_lists.insert(todo_list)

        response = client.post(
            get_api_url('/todo'),
            json={
                'title': 'title',
                'description': "description",
                'valid_until': (datetime.utcnow() + timedelta(days=7)).date().strftime('%Y-%m-%dT%H:%M:%S%z'),
                'todo_list_id': todo_list.id
            })

        base_response = get_base_response(response)
        assert base_response.success
        assert response.status_code == HTTPStatus.CREATED

        todo = uow.todos.get(base_response.data['id'])

        assert todo is not None
        assert todo.status_id == TodoStatuses.open.id
        assert todo.user_id == user.id

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_all_todos_not_empty_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = uow.todo_lists.all()[0]

        todo = Todo(
            title="_title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.closed.id
        )
        uow.todos.insert(todo)

        response = client.get(get_api_url('/todo'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == "Todo obtained."
        assert len(base_response.data) == 2

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_todo_not_available_case(self, client: FlaskClient):
        todo_id = str(uuid.uuid4())
        response = client.get(get_api_url(f'/todo/{todo_id}'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert base_response.message == 'Invalid todo.'

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_todo_available_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = uow.todo_lists.all()[0]

        todo = Todo(
            title="_title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.closed.id
        )
        uow.todos.insert(todo)

        response = client.get(get_api_url(f'/todo/{todo.id}'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == 'Todo obtained.'

        assert base_response.data['id'] == todo.id
        assert base_response.data['user_id'] == todo.user_id
        assert base_response.data['status_id'] == todo.status_id

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_update_todo_not_exist(self, client: FlaskClient, uow: UnitOfWork):
        todo_id = str(uuid.uuid4())
        todo_list = uow.todo_lists.all()[0]

        response = client.put(
            get_api_url(f'/todo/{todo_id}'),
            json={
                'title': '_title',
                'description': "description",
                'valid_until': (datetime.utcnow() + timedelta(days=7)).date().strftime('%Y-%m-%dT%H:%M:%S%z'),
                'todo_list_id': todo_list.id,
                'status_id': TodoStatuses.open.id
            })

        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert base_response.message == 'Invalid todo.'

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_update_todo_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = uow.todo_lists.all()[0]

        todo = Todo(
            title="_title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.closed.id
        )
        uow.todos.insert(todo)

        response = client.put(
            get_api_url(f'/todo/{todo.id}'),
            json={
                'title': '_title_changed',
                'description': "description",
                'valid_until': (datetime.utcnow() + timedelta(days=7)).date().strftime('%Y-%m-%dT%H:%M:%S%z'),
                'todo_list_id': todo_list.id,
                'status_id': TodoStatuses.open.id
            })

        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK

        db_todo = uow.todos.get(todo.id)

        assert db_todo.id == todo.id
        assert db_todo.title == "_title_changed"
        assert db_todo.user_id == todo.user_id
        assert db_todo.status_id == TodoStatuses.open.id

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_delete_todo_not_exist(self, client: FlaskClient):
        todo_id = str(uuid.uuid4())
        response = client.delete(get_api_url(f'/todo/{todo_id}'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert base_response.message == 'Invalid todo.'
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_delete_todo_already_deleted(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = uow.todo_lists.all()[0]

        todo = Todo(
            title="deleted_title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.deleted.id
        )
        uow.todos.insert(todo)

        response = client.delete(get_api_url(f'/todo/{todo.id}'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert base_response.message == 'Invalid todo.'

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_delete_todo_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = uow.todo_lists.all()[0]

        todo = Todo(
            title="title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.open.id
        )
        uow.todos.insert(todo)

        response = client.delete(get_api_url(f'/todo/{todo.id}'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK

        db_todo = uow.todos.get(todo.id)

        assert db_todo.id == todo.id
        assert db_todo.status == TodoStatuses.deleted
        assert db_todo.user_id == todo.user_id
        assert db_todo.title == todo.title
