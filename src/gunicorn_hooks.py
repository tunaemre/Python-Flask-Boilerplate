from typing import Dict, Any, Callable

from gunicorn.http import Request
from gunicorn.http.wsgi import Response
from gunicorn.workers.base import Worker
from gunicorn.app.base import Arbiter


class GunicornHooks:
    __pre_request_callbacks: Dict[str, Callable[[Request], None]] = dict()
    __post_request_callbacks: Dict[str, Callable[[Request, Dict[Any, Any]], None]] = dict()
    __shutdown_callbacks: Dict[str, Callable[..., None]] = dict()

    @staticmethod
    def add_pre_request_callback(name: str, callback: Callable[[Request], None]) -> None:
        GunicornHooks.__pre_request_callbacks[name] = callback

    @staticmethod
    def add_post_request_callback(name: str, callback: Callable[[Request, Dict[Any, Any]], None]) -> None:
        GunicornHooks.__post_request_callbacks[name] = callback

    @staticmethod
    def add_shutdown_callback(name: str, callback: Callable[..., None]) -> None:
        GunicornHooks.__shutdown_callbacks[name] = callback

    @staticmethod
    def pre_request(worker: Worker, req: Request) -> None:
        for n, c in GunicornHooks.__pre_request_callbacks.items():
            c(req)

    @staticmethod
    def post_request(worker: Worker, req: Request, environ: Dict[Any, Any], resp: Response) -> None:
        for n, c in GunicornHooks.__post_request_callbacks.items():
            c(req, environ)

    @staticmethod
    def worker_abort(worker: Worker) -> None:
        for n, c in GunicornHooks.__shutdown_callbacks.items():
            c()

    @staticmethod
    def worker_quit(worker: Worker) -> None:
        for n, c in GunicornHooks.__shutdown_callbacks.items():
            c()

    @staticmethod
    def worker_exit(server: Arbiter, worker: Worker) -> None:
        for n, c in GunicornHooks.__shutdown_callbacks.items():
            c()
        GunicornHooks.__clear_callbacks()

    @staticmethod
    def __clear_callbacks() -> None:
        GunicornHooks.__pre_request_callbacks.clear()
        GunicornHooks.__post_request_callbacks.clear()
        GunicornHooks.__shutdown_callbacks.clear()
