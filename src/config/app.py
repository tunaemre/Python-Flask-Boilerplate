from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Extra, Field

from src.config.base.base_config import BaseConfig
from src.config.scheme.mysql_dsn import MysqlDsn


class GlobalConfig(BaseConfig):
    @classmethod
    def create(cls, env_file: Optional[str]) -> GlobalConfig:
        cls.Config.env_file = env_file
        return cls()

    MYSQL_URL: MysqlDsn  # mysql+mysqldb://username:password@0.0.0.0:3306
    MYSQL_DB_NAME: str
    MYSQL_DB_CHARSET: str = Field('utf8mb4')

    SWAGGER_USERNAME: Optional[str]
    SWAGGER_PASSWORD: Optional[str]

    PROFILER_REQUEST_TIMER_THRESHOLD: int = Field(3, ge=0)  # seconds, 0 for disable
    PROFILER_QUERY_COUNTER_THRESHOLD: int = Field(10, ge=0)  # queries, 0 for disable

    PROPAGATE_EXCEPTIONS: Optional[bool] = Field(True)  # must be true to return api errors

    PROFILING_RATE: float = Field(0.0)

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
