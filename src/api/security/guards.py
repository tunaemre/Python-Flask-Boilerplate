from functools import wraps
from types import SimpleNamespace
from typing import Callable, TypeVar, Any, cast
from flask import g

from src.domain.common.error.authentication_errors import InvalidTokenError, PermissionDeniedError
from src.domain.user.errors.user_errors import DeactivatedUserError
from src.domain.user.entity.user import User
from src.domain.user.entity.user_status import UserStatuses
from src.infrastructure.manager.auth_manager import AuthManager
from src.infrastructure.manager.uow_manager import UOWManager

todo_scope = SimpleNamespace(
    read='read:todo',
    write='write:todo'
)

admin_scope = SimpleNamespace(
    admin='admin'
)

worker_scope = SimpleNamespace(
    worker='worker'
)

F = TypeVar('F', bound=Callable[..., Any])


def authorization_guard(*required_permissions: SimpleNamespace) -> Callable[..., F]:
    def decorator(function: F) -> F:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            auth0_service = AuthManager.get_auth()
            token = auth0_service.get_bearer_token_from_request()
            access_token = auth0_service.validate_jwt(token)

            if not access_token:
                raise InvalidTokenError

            token_sub = access_token.get("sub")
            if not token_sub:
                raise InvalidTokenError

            if access_token.get('gty') != 'client-credentials':
                # Not a machine to machine token
                user = check_user_if_not_upsert(token_sub, token)
                g.user = user

            if not required_permissions:
                return function(*args, **kwargs)

            token_permissions = access_token.get("permissions")

            if not token_permissions:
                raise PermissionDeniedError

            required_permissions_set = set(required_permissions)
            token_permissions_set = set(token_permissions)

            if not required_permissions_set.issubset(token_permissions_set):
                raise PermissionDeniedError

            return function(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def check_user_if_not_upsert(token_sub: str, token: str) -> User:
    uow = UOWManager.get_uow()
    with uow:
        user = uow.users.get_sub_id(token_sub)
        if not user:
            auth0_service = AuthManager.get_auth()
            user_info_response_dto = auth0_service.get_userinfo(token)

            user = uow.users.get_by_email(user_info_response_dto.email)
            if not user:
                user = User.create(user_info_response_dto.sub,
                                   user_info_response_dto.email)
                uow.users.insert(user)
            else:
                user.sub_id = user_info_response_dto.sub
                uow.users.update(user)

        if user.status_id != UserStatuses.enabled.id:
            raise DeactivatedUserError(user=user)

        return user
