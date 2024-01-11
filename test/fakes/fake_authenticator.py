import uuid
from contextlib import ContextDecorator
from typing import Dict, Any

from authlib.jose import JWSHeader
from authlib.oauth2.rfc7523 import JWTBearerToken

from src.api.models.dto.user_info_dto import UserInfoResponseDto
from src.config import app_config_manager
from test import test_user_email, test_user_sub_id


class _FakeAuthenticator:

    def __init__(self) -> None:
        self._token = None

    def validate_jwt(self, token: str) -> Dict[str, Any]:
        return self._token

    def get_bearer_token_from_request(self) -> str:
        return "TestToken"

    def get_userinfo(self, token: str) -> UserInfoResponseDto:
        user_info = UserInfoResponseDto(
            sub=test_user_sub_id,
            email=test_user_email
        )

        return user_info

    def set_token(self, token: JWTBearerToken) -> None:
        self._token = token

    def clear_token(self) -> None:
        self._token = None


fake_authenticator = _FakeAuthenticator()


class _FakePermission(ContextDecorator):
    def __init__(self, *permission: str) -> None:
        self.token = self.create_token_with_permission(*permission)

    def create_token_with_permission(self, *permission: str) -> JWTBearerToken:
        config = app_config_manager.get_config()
        token = JWTBearerToken(
            payload={
                'iss': f'https://{config.AUTH0_DOMAIN}/',
                'sub': test_user_sub_id,
                'aud': config.AUTH0_AUDIENCE,
                'iat': 1000000000,
                'exp': 9000000000,
                'azp': 'https://test.com',
                'permissions': permission
            },
            header=JWSHeader(
                protected={
                    'alg': 'RS256',
                    'typ': 'JWT',
                    'kid': str(uuid.uuid4())},
                header=None
            )
        )
        return token

    def __enter__(self) -> Any:
        fake_authenticator.set_token(self.token)
        return self

    def __exit__(self, *exc) -> None:
        fake_authenticator.clear_token()


fake_permission = _FakePermission
