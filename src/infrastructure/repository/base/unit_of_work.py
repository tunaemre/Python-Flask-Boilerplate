from __future__ import annotations

from functools import cached_property
from typing import Any, List, Optional

from flask import g
from sqlalchemy.orm import Session, scoped_session, SessionTransaction

from src.infrastructure.repository.todo.todo_repository import TodoRepository
from src.infrastructure.repository.todo_list.todo_list_repositories import TodoListRepository
from src.infrastructure.repository.user.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, scoped_session_factory: Optional[scoped_session] = None) -> None:
        if scoped_session_factory:
            self._scoped_session_factory = scoped_session_factory
        else:
            self._scoped_session_factory = g.get('scoped_session_factory')
        self._session_transactions: List[SessionTransaction] = []
        self._default_session: Optional[Session] = None

    def __enter__(self) -> UnitOfWork:
        # Close the default session if exists
        if self._default_session:
            self._default_session.close()
            self._default_session = None

        if not self._session_transactions:
            _session_transaction = self._scoped_session_factory.begin()
            self._session_transactions.append(_session_transaction)
        else:
            _nested_session_transaction = self._scoped_session_factory.begin_nested()
            self._session_transactions.append(_nested_session_transaction)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        _session_transaction = self._session_transactions.pop()
        try:
            if not isinstance(exc_value, Exception):
                _session_transaction.commit()
            else:
                _session_transaction.rollback()
        except Exception as ex:
            _session_transaction.rollback()
            raise Exception('An error occurred when performing DB operation.') from ex

        # Close scoped session factory if there is no active transaction left
        if not self._session_transactions:
            self._scoped_session_factory.remove()

    def session(self) -> Session:
        if self._session_transactions:
            # The last session in context is actually current session
            return self._session_transactions[-1].session

        # Create a default session if not exists
        if not self._default_session:
            self._default_session = self._scoped_session_factory()
        return self._default_session

    def commit(self) -> None:
        self.session().commit()

    def rollback(self) -> None:
        self.session().rollback()

    @cached_property
    def todos(self) -> TodoRepository:
        return TodoRepository(session_callable=self.session)

    @cached_property
    def users(self) -> UserRepository:
        return UserRepository(session_callable=self.session)

    @cached_property
    def todo_lists(self) -> TodoListRepository:
        return TodoListRepository(session_callable=self.session)
