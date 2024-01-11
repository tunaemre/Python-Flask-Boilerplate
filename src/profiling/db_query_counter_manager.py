import threading
from typing import Any, Optional

from flask import Flask, request

from src.config import app_config_manager
from src.profiling.db_query_counter import DBQueryCounter

_thread_local = threading.local()


class DBQueryCounterManager:

    @staticmethod
    def init_manager(app: Flask) -> None:
        if app_config_manager.get_config().PROFILER_QUERY_COUNTER_THRESHOLD < 1:
            return

        app.before_request(DBQueryCounterManager._start_flask_query_counting)
        app.teardown_request(DBQueryCounterManager._end_flask_query_counting)

    @staticmethod
    def create_query_counter(name: str, **kwargs: Any) -> DBQueryCounter:
        counter = DBQueryCounter(name, **kwargs)
        _thread_local.query_counter = counter
        return counter

    @staticmethod
    def get_query_counter() -> Optional[DBQueryCounter]:
        return getattr(_thread_local, 'query_counter', None)

    @staticmethod
    def remove_query_counter() -> None:
        try:
            delattr(_thread_local, 'query_counter')
        except AttributeError:
            pass

    @staticmethod
    def _start_flask_query_counting() -> None:
        DBQueryCounterManager.create_query_counter(
            f'{request.method} {request.path}')

    @staticmethod
    def _end_flask_query_counting(error: Any = None) -> None:
        if query_counter := DBQueryCounterManager.get_query_counter():
            query_counter.close()
            DBQueryCounterManager.remove_query_counter()


session_db_query_counter = DBQueryCounterManager.get_query_counter
