import threading
from typing import Any, Tuple

from flask import Flask, g
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.config import app_config_manager
from src.profiling.db_query_counter_manager import session_db_query_counter
from src.profiling.request_timer_manager import session_request_timer


class DBManager:

    @staticmethod
    def _get_engine_url() -> str:
        config = app_config_manager.get_config()
        url = config.MYSQL_URL.rstrip('/')  # Remove trailing "/" char
        url = f'{url}/{config.MYSQL_DB_NAME}?charset={config.MYSQL_DB_CHARSET}'
        return url

    @staticmethod
    def _create_session_factory(debug: bool = False) -> scoped_session:
        url = DBManager._get_engine_url()
        engine = create_engine(
            url,
            pool_timeout=5,
            pool_pre_ping=True,
            echo=debug
        )

        return scoped_session(
            session_factory=sessionmaker(bind=engine),
            scopefunc=threading.get_ident
        )

    @staticmethod
    def init_db(app: Flask) -> None:
        scoped_session_factory = DBManager._create_session_factory(debug=app.debug)

        def attach_scoped_session() -> None:
            """
            Called before each request.
            https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.before_request
            """
            if 'scoped_session_factory' not in g:
                g.scoped_session_factory = scoped_session_factory

        def remove_scoped_session(exp: Any) -> None:
            """
            Called when the application context is popped.
            https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.teardown_appcontext
            """
            if session_factory := g.pop('scoped_session_factory', None):
                session_factory.remove()

        # Register flask context events
        app.before_request(attach_scoped_session)
        app.teardown_appcontext(remove_scoped_session)

        def before_cursor_execute(
                connection: Connection,
                cursor: Any,
                statement: str,
                params: Tuple[Any],
                context: Any,
                executemany: bool) -> None:
            """
            Called before database query execution.
            https://docs.sqlalchemy.org/en/14/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute
            """
            if request_timer := session_request_timer():
                request_timer_context = request_timer('db_query', statement=statement)
                request_timer_context.open()
                connection.info.setdefault('request_timer_stack', []).append(request_timer_context)

            if query_counter := session_db_query_counter():
                query_counter(query=statement)

        def after_cursor_execute(connection: Connection, *args: Any) -> None:
            """
            Called after database query execution.
            https://docs.sqlalchemy.org/en/14/core/events.html#sqlalchemy.events.ConnectionEvents.after_cursor_execute
            """
            try:
                request_timer_context = connection.info['request_timer_stack'].pop(-1)
                request_timer_context.close()
            except (KeyError, IndexError):
                # request_timer_stack is not found or empty
                pass

        # Register low level database cursor events
        event.listen(Engine, 'before_cursor_execute', before_cursor_execute)
        event.listen(Engine, 'after_cursor_execute', after_cursor_execute)
