from flask import Flask

from src.config import get_environment, app_config_manager


class ProfilingHandler:

    @classmethod
    def initialize(cls, app: Flask) -> None:
        env = get_environment()

        if env in ('local', 'dev') and min(app_config_manager.get_config().PROFILING_RATE, 1) > 0:
            from src.profiling.profiling_middleware import ProfilingMiddleware
            app.wsgi_app = ProfilingMiddleware(  # type: ignore
                app=app,
                rate=min(app_config_manager.get_config().PROFILING_RATE, 1),  # rate must be a float in 0.0-1.0 range
                sort_by=['time', 'calls'])
