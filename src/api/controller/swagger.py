from typing import Any

from flask import Blueprint, request, Flask
from flask_httpauth import HTTPBasicAuth
from flask_restx import Api

from src.config import get_environment, app_config_manager


class SwaggerManager:

    @staticmethod
    def init_swagger(app: Flask, *blueprints: Blueprint) -> None:
        authenticator = None
        if get_environment() != 'local':
            authenticator = _SwaggerAuthenticator(app)

        authorizations = {
            'api_key': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'authorization'
            }
        }

        for blueprint in blueprints:
            api = Api(
                blueprint,
                title=blueprint.name
            )
            if hasattr(blueprint, '_namespaces'):
                for n in getattr(blueprint, '_namespaces'):
                    n.authorizations = authorizations
                    api.add_namespace(n)
            if authenticator:
                authenticator.secure(api)


class _SwaggerAuthenticator:
    def __init__(self, app: Flask) -> None:
        config = app_config_manager.get_config()
        self.app = app
        self.username = config.SWAGGER_USERNAME
        self.password = config.SWAGGER_PASSWORD

        auth = HTTPBasicAuth()
        auth.verify_password(self.verify_password)
        self.auth = auth

    def verify_password(self, username: str, password: str) -> bool:
        return username == self.username and password == self.password

    def secure(self, api: Api) -> None:
        doc_path = api.blueprint.url_prefix.rstrip('/')  # Remove trailing "/" char
        json_path = doc_path + '/swagger.json'

        def _check_auth() -> Any:
            if not request.endpoint:
                return

            request_path = request.path.rstrip('/')  # Remove trailing "/" char
            if request_path == doc_path or request_path == json_path:
                view = self.app.view_functions[request.endpoint]
                return self.auth.login_required(view)()

        self.app.before_request(_check_auth)
