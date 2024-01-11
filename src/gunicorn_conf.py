import os
from src.gunicorn_hooks import GunicornHooks


_web_concurrency = int(os.getenv('WEB_CONCURRENCY', 0))
if _web_concurrency == 0:
    import multiprocessing
    _cpu_count = multiprocessing.cpu_count()
    _web_concurrency = _cpu_count * 2 + 1
workers = _web_concurrency
threads = os.getenv('WEB_THREAD', 2)
worker_class = os.getenv('WORKER_CLASS', 'gthread')

timeout = os.getenv('WORKER_TIMEOUT', 28)
graceful_timeout = os.getenv('WORKER_GRACEFUL_TIMEOUT', 29)

preload_app = os.getenv('WORKER_PRELOAD_APP', False)

max_requests = int(os.getenv('WORKER_MAX_REQUESTS', 0))
_max_requests_jitter = int(os.getenv('WORKER_MAX_REQUESTS_JITTER', 0))
if max_requests > 0 and _max_requests_jitter == 0:
    _max_requests_jitter = 50
max_requests_jitter = _max_requests_jitter

pre_request = GunicornHooks.pre_request
post_request = GunicornHooks.post_request
worker_abort = GunicornHooks.worker_abort
worker_int = GunicornHooks.worker_quit
worker_exit = GunicornHooks.worker_exit
