import pytest
from typing import Generator, Any

import os

from _pytest.main import Session
from celery import Celery
from flask import Flask
from sqlalchemy_utils import drop_database, create_database, database_exists

from src.infrastructure.entity.base import mapper_registry
from src.infrastructure.manager.auth_manager import AuthManager
from src.infrastructure.manager.db_manager import DBManager
from src.infrastructure.manager.uow_manager import UOWManager
from src.infrastructure.repository.base.unit_of_work import UnitOfWork
from test import test_user_email, test_user_sub_id
from test.fakes.fake_authenticator import fake_authenticator

os.environ["ENVIRONMENT"] = "test"

from src.worker import celery as celery_instance
from src.app import create_app


# Initial test session start tasks
def pytest_sessionstart(session: Session) -> None:
    scoped_session_factory = DBManager._create_session_factory()
    engine = scoped_session_factory.bind
    database_url = engine.url
    if database_exists(database_url):
        drop_database(database_url)

    create_database(database_url)
    mapper_registry.metadata.create_all(engine)
    UOWManager._uow = UnitOfWork(scoped_session_factory=scoped_session_factory)

    seed_statuses()
    create_test_user()
    inject_fakes()


# After finish test session
def pytest_sessionfinish(session: Session, exitstatus: int) -> None:
    if uow := UOWManager._uow:
        uow._scoped_session_factory.remove()
        drop_database(str(uow._scoped_session_factory.bind.url))


@pytest.fixture(scope='session')
def app() -> Flask:
    return create_app()


@pytest.fixture(scope='class')
def db_session() -> Generator[Session, Any, None]:
    uow = UOWManager.get_uow()
    _session_transaction = uow._scoped_session_factory.begin()
    uow._session_transactions.append(_session_transaction)
    yield _session_transaction
    if _session_transaction.is_active:
        _session_transaction.rollback()


@pytest.fixture(scope='function')
def uow() -> UnitOfWork:
    return UOWManager.get_uow()


@pytest.fixture(scope='function')
def celery() -> Generator[Celery, Any, None]:
    celery_instance.conf.update(
        task_always_eager=True,
        task_eager_propagates=True
    )
    yield celery_instance
    celery_instance.conf.update(
        task_always_eager=False,
        task_eager_propagates=False
    )


def seed_statuses() -> None:
    from src.domain.todo.entity.todo_status import TodoStatuses
    from src.domain.user.entity.user_status import UserStatuses
    from src.domain.todo_list.entity.todo_list_status import TodoListStatuses

    from src.infrastructure.entity.todo.todo_status import TodoStatus
    from src.infrastructure.entity.user.user_status import UserStatus
    from src.infrastructure.entity.todo_list.todo_list_status import TodoListStatus

    uow = UOWManager.get_uow()
    with uow:
        uow.session().add_all([TodoStatus.from_dict(s.dict()) for s in TodoStatuses.get_all()])
        uow.session().add_all([UserStatus.from_dict(s.dict()) for s in UserStatuses.get_all()])
        uow.session().add_all([TodoListStatus.from_dict(s.dict()) for s in TodoListStatuses.get_all()])


def create_test_user():
    from src.domain.user.entity.user import User as DomainUser
    from src.infrastructure.entity.user.user import User

    user = DomainUser.create(test_user_email, test_user_sub_id)

    uow = UOWManager.get_uow()
    with uow:
        uow.session().add(User.from_model(user))


def inject_fakes() -> None:
    AuthManager._auth = fake_authenticator
