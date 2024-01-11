import threading
from typing import Any, Dict, Optional, Union

from flask import Flask, request, g, has_app_context

from src.config import app_config_manager
from src.profiling.request_timer import RequestTimer, _RequestTimerContext, _MockTimerContext

_thread_local = threading.local()


class RequestTimerManager:

    @staticmethod
    def init_manager(app: Flask) -> None:
        if app_config_manager.get_config().PROFILER_REQUEST_TIMER_THRESHOLD < 1:
            return

        with app.app_context():
            RequestTimerManager._init_gunicorn_hooks()
            app.before_request(RequestTimerManager._start_flask_request_timing)
            app.teardown_request(RequestTimerManager._end_flask_request_timing)

    @staticmethod
    def get_request_timer() -> Optional[RequestTimer]:
        return getattr(_thread_local, 'request_timer', None)

    @staticmethod
    def create_request_timer(name: str, **kwargs: Any) -> RequestTimer:
        timer = RequestTimer(name, **kwargs)
        _thread_local.request_timer = timer
        return timer

    @staticmethod
    def get_request_timer_context(key: str, **kwargs: Any) -> Union[_RequestTimerContext, _MockTimerContext]:
        timer = RequestTimerManager.get_request_timer()
        if timer:
            return timer(key, **kwargs)
        else:
            return _MockTimerContext()

    @staticmethod
    def remove_request_timer() -> None:
        try:
            delattr(_thread_local, 'request_timer')
        except AttributeError:
            pass

    @staticmethod
    def _init_gunicorn_hooks() -> None:
        from src.gunicorn_hooks import GunicornHooks
        GunicornHooks.add_pre_request_callback(
            'gunicorn_pre_request',
            RequestTimerManager._gunicorn_pre_request
        )
        GunicornHooks.add_post_request_callback(
            'gunicorn_post_request',
            RequestTimerManager._gunicorn_post_request
        )
        GunicornHooks.add_shutdown_callback(
            'gunicorn_shutdown',
            RequestTimerManager._gunicorn_shutdown
        )

    @staticmethod
    def _start_flask_request_timing() -> None:
        request_timer = RequestTimerManager.get_request_timer()
        if not request_timer:
            request_timer = RequestTimerManager.create_request_timer(
                f'{request.method} {request.path}'
            )
        context = request_timer('flask_request')
        context.open()
        g.timer_context = context

    @staticmethod
    def _end_flask_request_timing(error: Any = None) -> None:
        if not has_app_context():
            return

        if timer_context := getattr(g, 'timer_context', None):
            timer_context.close()

        if request_timer := RequestTimerManager.get_request_timer():
            request_timer.try_to_close(
                'flask_request',
                on_close=RequestTimerManager.remove_request_timer
            )

    @staticmethod
    def _gunicorn_pre_request(req: Any) -> None:
        # req: Gunicorn.HTTP.Request
        timer = RequestTimerManager.create_request_timer(
            f'{req.method} {req.path}')
        timer_context = timer('gunicorn_request')
        timer_context.open()

    @staticmethod
    def _gunicorn_post_request(req: Any, environ: Dict[Any, Any]) -> None:
        # req: Gunicorn.HTTP.Request
        if request_timer := RequestTimerManager.get_request_timer():
            request_timer.try_to_close(
                'gunicorn_request',
                on_close=RequestTimerManager.remove_request_timer
            )

    @staticmethod
    def _gunicorn_shutdown() -> None:
        if request_timer := RequestTimerManager.get_request_timer():
            request_timer.force_close()
            RequestTimerManager.remove_request_timer()


session_request_timer = RequestTimerManager.get_request_timer
session_request_timer_context = RequestTimerManager.get_request_timer_context
