from typing import List, Tuple

from flask import Response
from flask_restx import Namespace, Resource

from src.api.models.base_response import BaseResponse
from src.api.security.guards import authorization_guard, worker_scope
from src.api.services.todo_worker_service import TodoWorkerService
from src.domain.todo.entity.todo import Todo
from src.domain.user.entity.user import User

namespace = Namespace(
    'Worker API',
    description='API for Worker',
    path='/worker')


# response dto
todo_user_list_response_schema = namespace.schema_model(
    'todo_user_list_response_schema', BaseResponse[List[Tuple[Todo, User]]].schema())


@namespace.route('/expired')
class UpdateExpiredController(Resource):
    @namespace.doc(description='Updates expired todos', security='api_key')
    @namespace.response(200, 'OK', todo_user_list_response_schema)
    @authorization_guard(worker_scope.worker)
    def put(self) -> Response:
        service = TodoWorkerService()
        todo_user_list = service.update_expired_todos()

        message = 'Expired todos updated.' if todo_user_list \
            else 'No expired todo found.'
        return BaseResponse.create_response(message=message, data=todo_user_list)
