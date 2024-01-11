from typing import Optional
from redis import Redis

from src.config import get_environment
from src.config.base.base_config import BaseConfig
from src.domain.common.error.configuration_error import ConfigurationError


class RedisManager:
    __redis_instance: Optional[Redis] = None  # type: ignore

    @classmethod
    def init_redis(cls, config: BaseConfig) -> None:
        env = get_environment()

        if config.REDIS_HOST and config.REDIS_PORT:
            # No check for REDIS_PASSWORD and REDIS_DB in local and test env
            if env in ('test', 'local') or config.REDIS_PASSWORD:
                cls.__redis_instance = Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    password=config.REDIS_PASSWORD,
                    db=config.REDIS_DB,
                    decode_responses=True)

    @classmethod
    def get_redis(cls) -> Redis:  # type: ignore
        if not cls.__redis_instance:
            raise ConfigurationError('Redis is not initialized.', 'redis_not_initialized')
        return cls.__redis_instance
