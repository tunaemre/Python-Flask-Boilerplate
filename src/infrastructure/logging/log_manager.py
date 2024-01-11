import logging
import graypy

from src.config import get_environment
from src.config.base.base_config import BaseConfig
from src.infrastructure.logging.environment_filter import EnvironmentFilter


class LogManager:

    @staticmethod
    def init_logger(config: BaseConfig) -> None:
        env = get_environment()

        logger = logging.getLogger()

        logger.setLevel(config.GRAYLOG_LOGGING_LEVEL)
        logging.getLogger('werkzeug').setLevel(config.GRAYLOG_LOGGING_LEVEL)

        if env != 'local' and config.ENABLE_GRAYLOG and config.GRAYLOG_IP and config.GRAYLOG_PORT:
            handler = graypy.GELFUDPHandler(config.GRAYLOG_IP, config.GRAYLOG_PORT)

            environment_filter = EnvironmentFilter(environment=env)
            handler.addFilter(environment_filter)

            logger.addHandler(handler)
