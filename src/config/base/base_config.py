from __future__ import annotations

from pydantic import BaseSettings, Field
from typing import Optional
import logging


class BaseConfig(BaseSettings):

    """Base Configuration"""

    """Secrets"""
    GRAYLOG_IP: Optional[str]
    GRAYLOG_PORT: Optional[int]

    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str

    REDIS_HOST: Optional[str]
    REDIS_PORT: Optional[int]
    REDIS_PASSWORD: Optional[str]
    REDIS_DB: int = Field(0)

    """Configurations"""
    ENABLE_GRAYLOG: bool = Field(True)
    GRAYLOG_LOGGING_LEVEL: int = Field(logging.INFO)

    REDIS_TODOS_PREFIX: str = Field('todo')
    REDIS_TODO_LISTS_PREFIX: str = Field('todo_lists')

