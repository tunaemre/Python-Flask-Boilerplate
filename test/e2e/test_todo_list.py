import pytest
import uuid
from src.api.security.guards import todo_scope
from flask.testing import FlaskClient
from http import HTTPStatus
from datetime import datetime
from src.domain.todo.entity.todo import Todo
from src.domain.todo.entity.todo_status import TodoStatuses
from src.domain.todo_list.entity.todo_list import TodoList
from src.domain.todo_list.entity.todo_list_status import TodoListStatuses
from src.infrastructure.repository.base.unit_of_work import UnitOfWork
from test import test_user_email
from test.e2e import get_api_url, get_base_response
from test.fakes.fake_authenticator import fake_permission


@pytest.mark.usefixtures('client', 'db_session')
class TestTodoListController:

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_all_todo_lists_empty_case(self, client: FlaskClient):
        response = client.get(get_api_url('/todo_list'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == "No todolist found."
        assert base_response.data == []

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_all_todo_lists_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)

        todo_list = TodoList(
            name="test_todo_list",
            user_id=user.id,
            status_id=TodoListStatuses.open.id
        )
        uow.todo_lists.insert(todo_list)

        response = client.get(get_api_url('/todo_list'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == "Todolist obtained."
        assert len(base_response.data) == 1

        assert base_response.data[0]['id'] == todo_list.id
        assert base_response.data[0]['user_id'] == todo_list.user_id
        assert base_response.data[0]['status_id'] == todo_list.status_id

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_create_todo_list_dto_error(self, client: FlaskClient):
        response = client.post(
            get_api_url('/todo_list'),
            json={
                'name_': "test_todo_list"
            })

        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_create_todo_list_success_case(self, client: FlaskClient, uow: UnitOfWork):
        response = client.post(
            get_api_url('/todo_list'),
            json={
                'name': "test_todo_list"
            })

        base_response = get_base_response(response)
        assert base_response.success
        assert response.status_code == HTTPStatus.CREATED

        todo_list = uow.todo_lists.get(base_response.data['id'])

        user = uow.users.get_by_email(test_user_email)
        assert todo_list is not None
        assert todo_list.status_id == TodoListStatuses.open.id
        assert todo_list.user_id == user.id

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_todo_list_not_available_case(self, client: FlaskClient):
        todo_list_id = str(uuid.uuid4())
        response = client.get(get_api_url(f'/todo_list/{todo_list_id}'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert base_response.message == 'Invalid todo list.'

    @fake_permission(todo_scope.read)  # Set token with read permission
    def test_get_todo_list_available_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)

        todo_list = TodoList(
            name="_name",
            user_id=user.id,
            status_id=TodoListStatuses.closed.id
        )
        uow.todo_lists.insert(todo_list)

        todo = Todo(
            title="_title",
            description="description",
            valid_until=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            user_id=user.id,
            todo_list_id=todo_list.id,
            status_id=TodoStatuses.open.id
        )
        uow.todos.insert(todo)

        response = client.get(get_api_url(f'/todo_list/{todo_list.id}'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert base_response.message == 'Todo list obtained.'

        assert base_response.data['id'] == todo_list.id
        assert base_response.data['user_id'] == todo_list.user_id
        assert base_response.data['status_id'] == todo_list.status_id

        assert base_response.data['todos'][0]['id'] == todo.id
        assert base_response.data['todos'][0]['user_id'] == todo.user_id
        assert base_response.data['todos'][0]['status_id'] == todo.status_id

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_update_todo_not_exist(self, client: FlaskClient):
        todo_list_id = str(uuid.uuid4())
        response = client.put(
            get_api_url(f'/todo_list/{todo_list_id}'),
            json={
                'name': '_name',
                'status_id': TodoListStatuses.open.id
            })

        base_response = get_base_response(response)

        assert not base_response.success
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert base_response.message == 'Invalid todo list.'

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_update_todo_list_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)
        todo_list = TodoList(
            name="_name_changed",
            user_id=user.id,
            status_id=TodoListStatuses.closed.id
        )
        uow.todo_lists.insert(todo_list)

        response = client.put(
            get_api_url(f'/todo_list/{todo_list.id}'),
            json={
                'name': '_name_changed',
                'status_id': TodoListStatuses.open.id
            })

        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK

        db_todo = uow.todo_lists.get(todo_list.id)

        assert db_todo.id == todo_list.id
        assert db_todo.name == "_name_changed"
        assert db_todo.user_id == todo_list.user_id
        assert db_todo.status_id == TodoListStatuses.open.id

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_delete_todo_list_not_exist(self, client: FlaskClient):
        todo_list_id = str(uuid.uuid4())
        response = client.delete(get_api_url(f'/todo_list/{todo_list_id}'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert base_response.message == 'Invalid todo list.'
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @fake_permission(todo_scope.write)  # Set token with write permission
    def test_delete_todo_list_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)

        todo_list = TodoList(
            name="name",
            user_id=user.id,
            status_id=TodoListStatuses.open.id
        )
        uow.todo_lists.insert(todo_list)

        response = client.delete(get_api_url(f'/todo_list/{todo_list.id}'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK

        db_todo_list = uow.todo_lists.get(todo_list.id)

        assert db_todo_list.id == todo_list.id
        assert db_todo_list.user_id == todo_list.user_id
        assert db_todo_list.name == todo_list.name
