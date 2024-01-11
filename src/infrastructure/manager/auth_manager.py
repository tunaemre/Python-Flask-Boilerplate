from typing import Optional

from src.api.security.auth0_service import Auth0Service


class AuthManager:
    _auth: Optional[Auth0Service] = None

    @classmethod
    def get_auth(cls) -> Auth0Service:
        if cls._auth is None:
            cls._auth = Auth0Service()
        return cls._auth
