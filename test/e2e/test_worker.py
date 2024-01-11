import random
from datetime import datetime
from http import HTTPStatus

import pytest
from dateutil.relativedelta import relativedelta
from flask.testing import FlaskClient

from src.api.security.guards import worker_scope, todo_scope
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
class TestWorkerController:

    @fake_permission(todo_scope.write)  # Set token without worker permission
    def test_update_expired_todos_forbidden(self, client: FlaskClient):
        response = client.put(get_api_url('/worker/expired'))
        base_response = get_base_response(response)

        assert not base_response.success
        assert base_response.code == PermissionDeniedError.code
        assert response.status_code == HTTPStatus.FORBIDDEN

    @fake_permission(worker_scope.worker)  # Set token with worker permission
    def test_update_expired_todos_empty_case(self, client: FlaskClient):
        response = client.put(get_api_url('/worker/expired'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert len(base_response.data) == 0

    @fake_permission(worker_scope.worker)  # Set token with worker permission
    def test_update_expired_todos_success_case(self, client: FlaskClient, uow: UnitOfWork):
        user = uow.users.get_by_email(test_user_email)

        todo_list = TodoList(
            name="name",
            user_id=user.id,
            status_id=TodoListStatuses.open.id
        )
        uow.todo_lists.insert(todo_list)

        _expired_count = random.randint(5, 10)
        for _ in range(_expired_count):
            todo = Todo(
                title="title",
                description="description",
                valid_until=datetime.utcnow() - relativedelta(hours=random.randint(1, 24)),
                user_id=user.id,
                todo_list_id=todo_list.id,
                status_id=TodoStatuses.open.id
            )
            uow.todos.insert(todo)

        _not_expired_count = random.randint(5, 10)
        for _ in range(_expired_count):
            todo = Todo(
                title="title",
                description="description",
                valid_until=datetime.utcnow() + relativedelta(hours=random.randint(1, 24)),
                user_id=user.id,
                todo_list_id=todo_list.id,
                status_id=TodoStatuses.open.id
            )
            uow.todos.insert(todo)

        response = client.put(get_api_url('/worker/expired'))
        base_response = get_base_response(response)

        assert base_response.success
        assert response.status_code == HTTPStatus.OK
        assert len(base_response.data) == _expired_count
