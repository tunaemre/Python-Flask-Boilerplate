from typing import Dict, Any

import jwt
from flask import request
import requests

from src.api.models.dto.user_info_dto import UserInfoResponseDto
from src.config import app_config_manager
from src.domain.common.error.authentication_errors import InvalidTokenError


class Auth0Service:
    """Perform JSON Web Token (JWT) validation using PyJWT"""

    def __init__(self) -> None:
        self.config = app_config_manager.get_config()
        self.algorithm = ['RS256']
        self.issuer_url = f'https://{self.config.AUTH0_DOMAIN}/'
        self.jwks_uri = f'{self.issuer_url}.well-known/jwks.json'
        self.audience = self.config.AUTH0_AUDIENCE

    def get_signing_key(self, token: str) -> str:
        try:
            if not self.jwks_uri:
                raise Exception("Initialize Auth Service Error ")
            jwks_client = jwt.PyJWKClient(self.jwks_uri)

            return jwks_client.get_signing_key_from_jwt(token).key
        except Exception:
            raise InvalidTokenError

    def validate_jwt(self, token: str) -> Dict[str, Any]:
        try:
            jwt_signing_key = self.get_signing_key(token)

            payload = jwt.decode(
                token,
                jwt_signing_key,
                algorithms=self.algorithm,
                audience=self.audience,
                issuer=self.issuer_url,
            )
        except Exception:
            raise InvalidTokenError

        return payload

    def get_bearer_token_from_request(self) -> str:
        authorization_header = request.headers.get("Authorization", None)

        if not authorization_header:
            raise InvalidTokenError

        authorization_header_elements = authorization_header.split()

        if len(authorization_header_elements) != 2:
            raise InvalidTokenError

        auth_scheme = authorization_header_elements[0]
        bearer_token = authorization_header_elements[1]

        if not (auth_scheme and auth_scheme.lower() == "bearer"):
            raise InvalidTokenError

        if not bearer_token:
            raise InvalidTokenError

        return bearer_token

    def get_userinfo(self, token: str) -> UserInfoResponseDto:
        response = requests.post(f'{self.issuer_url}userinfo',
                                 headers={f'Authorization': f'Bearer {token}'},
                                 timeout=4.0)

        return UserInfoResponseDto.parse_obj(response.json())
