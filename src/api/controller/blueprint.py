from typing import List, Any

from flask import Flask, Blueprint
from flask_restx import Namespace

from src.api.controller.swagger import SwaggerManager


class BlueprintManager:

    @staticmethod
    def register_blueprints(app: Flask) -> None:
        blueprints = BlueprintManager._blueprints()
        SwaggerManager.init_swagger(app, *blueprints)

        for b in blueprints:
            app.register_blueprint(b)

    @staticmethod
    def _blueprints() -> List[Blueprint]:
        def create_blueprint(name: str, url_prefix: str, *namespaces: Namespace, **kwargs: Any) -> Blueprint:
            b = Blueprint(name, __name__, url_prefix=url_prefix, **kwargs)
            setattr(b, '_namespaces', namespaces)
            return b

        bs = []

        from src.api.controller.todo.todo_controller import namespace as todo_namespace
        from src.api.controller.todo_list.todo_list_controller import namespace as todo_list_namespace
        from src.api.controller.worker.worker_controller import namespace as worker_namespace
        bs.append(
            create_blueprint('API', '/api/v1', todo_namespace, todo_list_namespace, worker_namespace)
        )
        return bs
