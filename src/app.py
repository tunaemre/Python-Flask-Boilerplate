from flask import Flask

from src.config import app_config_manager, get_environment


def create_app() -> Flask:
    app = Flask(__name__)
    app.debug = get_environment() == 'local'

    app.config.from_object(app_config_manager.get_config())

    from src.api.helpers.error_handler import ErrorHandler
    ErrorHandler.initialize(app)

    from src.infrastructure.logging.log_manager import LogManager
    LogManager.init_logger(app_config_manager.get_config())

    from src.api.controller.blueprint import BlueprintManager
    BlueprintManager.register_blueprints(app)

    from src.infrastructure.manager.db_manager import DBManager
    DBManager.init_db(app)

    from src.infrastructure.manager.db_migration_manager import DBMigrationManager
    DBMigrationManager.init_migration(app)

    from flask_cors import CORS
    CORS(app)

    from src.infrastructure.manager.redis_manager import RedisManager
    RedisManager.init_redis(app_config_manager.get_config())

    from src.profiling.request_timer_manager import RequestTimerManager
    RequestTimerManager.init_manager(app)

    from src.profiling.db_query_counter_manager import DBQueryCounterManager
    DBQueryCounterManager.init_manager(app)

    from src.profiling.profiling_handler import ProfilingHandler
    ProfilingHandler.initialize(app)

    from src.api.helpers.orm_event_manager import OrmEventManager
    OrmEventManager.init()

    return app
