from http import HTTPStatus

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError
from requests_mock import Mocker

from src.api.security.guards import worker_scope
from src.config import worker_config_manager
from src.task.beats import beat_check_expired_todos
from test.fakes.fake_authenticator import fake_permission
from test.tasks import get_mocker_response


@pytest.mark.usefixtures('celery')
class TestCheckExpiredTodos:
    _mocker_response_path = 'test_check_expired_todos'

    @fake_permission(worker_scope.worker)  # Set token with worker permission
    def test_check_expired_todos_empty(self,  requests_mock: Mocker, mocker: MockerFixture):
        requests_mock.post(
            f'https://{worker_config_manager.get_config().AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        requests_mock.put(
            f'{worker_config_manager.get_config().TODO_API_URL}/api/v1/worker/expired',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='check_expired_todos-empty'
            )
        )

        _mocked_send_expired_mail = mocker.patch('src.task.mail.tasks.send_expired_mail.delay',
                                                 return_value=True)
        beat_check_expired_todos.delay()

        assert not _mocked_send_expired_mail.called
        assert _mocked_send_expired_mail.call_count == 0

    @fake_permission(worker_scope.worker)  # Set token with worker permission
    def test_check_expired_todos_success(self, requests_mock: Mocker, mocker: MockerFixture):
        requests_mock.post(
            f'https://{worker_config_manager.get_config().AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        requests_mock.put(
            f'{worker_config_manager.get_config().TODO_API_URL}/api/v1/worker/expired',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='check_expired_todos-success'
            )
        )

        _mocked_send_expired_mail = mocker.patch('src.task.mail.tasks.send_expired_mail.delay',
                                                 return_value=True)

        beat_check_expired_todos.delay()

        assert _mocked_send_expired_mail.called
        assert _mocked_send_expired_mail.call_count == 8

    @fake_permission(worker_scope.worker)  # Set token with worker permission
    def test_check_expired_todos_error(self, requests_mock: Mocker, mocker: MockerFixture):
        requests_mock.post(
            f'https://{worker_config_manager.get_config().AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        requests_mock.put(
            f'{worker_config_manager.get_config().TODO_API_URL}/api/v1/worker/expired',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

        with pytest.raises(HTTPError):
            beat_check_expired_todos.delay()
