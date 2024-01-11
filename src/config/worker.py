from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Extra, PositiveInt, AmqpDsn


from src.config.base.base_config import BaseConfig


class GlobalConfig(BaseConfig):
    @classmethod
    def create(cls, env_file: Optional[str]) -> GlobalConfig:
        cls.Config.env_file = env_file
        return cls()

    BROKER_URL: AmqpDsn  # amqp://username:password@0.0.0.0:5672

    AUTH0_M2M_CLIENT_ID: str
    AUTH0_M2M_CLIENT_SECRET: str

    BEAT_CHECK_EXPIRED_TODOS_INTERVAL: int = PositiveInt(1)
    EXPIRE_TIME_OF_TASKS: int = PositiveInt(60)

    TODO_API_URL: str

    MAIL_SENDER_API_KEY: Optional[str]

    class Config(BaseSettings.Config):
        extra: Extra = Extra.ignore
        env_file: Optional[str] = None


class _ConfigManager:
    __config: Optional[GlobalConfig] = None

    @staticmethod
    def __get_dot_env() -> Optional[str]:
        from src.config import get_environment
        env = get_environment()
        env_path = os.path.join(Path(__file__).parent.parent.parent.absolute(), 'env', f'{env}.env')
        if os.path.exists(env_path):
            return env_path
        else:
            return None

    @classmethod
    def get_config(cls) -> GlobalConfig:
        if not cls.__config:
            cls.__config = GlobalConfig.create(cls.__get_dot_env())
        return cls.__config
