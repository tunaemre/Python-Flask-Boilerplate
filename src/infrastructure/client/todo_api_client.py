from datetime import datetime
from typing import Optional, Any, TypeVar, Type, List, Tuple, Final
from urllib.parse import urljoin

import requests
from dateutil.relativedelta import relativedelta
from requests import PreparedRequest, Response
from requests.auth import AuthBase

from src.api.models.base_response import BaseResponse
from src.config import worker_config_manager
from src.domain.todo.entity.todo import Todo
from src.domain.user.entity.user import User

Model = TypeVar('Model')


class TodoApiAuthBase(AuthBase):
    def __init__(self, token: str, expires_in: int) -> None:
        self.token = token
        self.expired_at = datetime.utcnow() + relativedelta(seconds=expires_in)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expired_at

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r


class TodoApiClient:
    __auth: Optional[TodoApiAuthBase] = None
    __default_timeout: Final = 4.0

    __update_expired_todos_url: Final = 'api/v1/worker/expired'

    @staticmethod
    def __get_endpoint(service_url: str) -> str:
        base_url = worker_config_manager.get_config().TODO_API_URL
        return urljoin(base_url, service_url)

    def __get_auth(self) -> TodoApiAuthBase:
        if not self.__auth or self.__auth.is_expired:
            token, expires_in = self.__get_token()
            self.__auth = TodoApiAuthBase(token=token, expires_in=expires_in)

        return self.__auth

    def __get_token(self) -> Tuple[str, int]:
        config = worker_config_manager.get_config()
        token_request = {
            'client_id': config.AUTH0_M2M_CLIENT_ID,
            'client_secret': config.AUTH0_M2M_CLIENT_SECRET,
            'audience': config.AUTH0_AUDIENCE,
            'grant_type': 'client_credentials'
        }

        response = requests.post(
            f'https://{worker_config_manager.get_config().AUTH0_DOMAIN}/oauth/token',
            json=token_request,
            timeout=self.__default_timeout)
        response.raise_for_status()

        data = response.json()
        return data['access_token'], data['expires_in']

    def __clear_auth(self) -> None:
        self.__auth = None

    def __check_response(self, response: Response) -> None:
        response = self.__check_unauthorized(response)
        response.raise_for_status()
        if response.content:
            base_response = BaseResponse[Any].parse_obj(response.json())
            if not base_response.success:
                raise Exception(f'Todo API error, message: {base_response.message}')

    def __check_response_and_get_data(self, response: Response, model: Type[Model]) -> Optional[Model]:
        response = self.__check_unauthorized(response)
        response.raise_for_status()
        base_response = BaseResponse[model].parse_obj(response.json())  # type: ignore
        if not base_response.success:
            raise Exception(f'Todo API error, message: {base_response.message}')
        return base_response.data

    def __check_unauthorized(self, response: Response) -> Response:
        if response.status_code == 401:
            # Renew auth
            self.__clear_auth()
            request = response.request.copy()
            request.prepare_auth(self.__get_auth())
            with requests.session() as s:
                response = s.send(request)
        return response

    def update_expired_todos(self) -> Optional[List[Tuple[Todo, User]]]:
        endpoint = self.__get_endpoint(self.__update_expired_todos_url)
        response = requests.put(endpoint,
                                auth=self.__get_auth(),
                                timeout=self.__default_timeout)

        data = self.__check_response_and_get_data(response, List[Tuple[Todo, User]])
        return data
