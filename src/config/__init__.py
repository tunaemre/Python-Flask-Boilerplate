import os

from src.config.app import _ConfigManager as AppConfigManager
from src.config.worker import _ConfigManager as WorkerConfigManager

app_config_manager = AppConfigManager
worker_config_manager = WorkerConfigManager


def get_environment() -> str:
    return os.environ.get('ENVIRONMENT') or 'local'
