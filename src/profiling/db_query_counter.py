import logging
from typing import Any, List, Dict, Optional
from uuid import uuid4

from src.config import get_environment, app_config_manager
from src.profiling.logger_adapter import ProfilingLoggerAdapter

logger = logging.getLogger(__name__)


class _DBQueryCounterStack:
    def __init__(self) -> None:
        self.items: List[str] = []

    def append(self, item: str) -> None:
        self.items.append(item)

    def logs(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        profile_total_queries = self.total  # profile total queries
        while stack_item := self.pop():
            items.append(
                {
                    'profile_total_queries': profile_total_queries,
                    'profile_query': stack_item
                }
            )
        return items

    def pop(self) -> Optional[str]:
        try:
            return self.items.pop(0)
        except IndexError:
            return None

    @property
    def total(self) -> int:
        return len(self.items)


class DBQueryCounter:
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.uuid = str(uuid4())
        self.stack = _DBQueryCounterStack()
        self.query_count_logger_adapter = ProfilingLoggerAdapter(
            logger,
            extra={**{'query_counter_log': 1,
                      'query_counter_uuid': self.uuid,
                      'environment': get_environment()},
                   **kwargs})
        self._is_closed = False

    def __call__(self, query: str) -> None:
        self.stack.append(query)

    def close(self) -> None:
        if self._is_closed:
            return
        self._is_closed = True
        # finalize request query counter
        if self.stack.total < app_config_manager.get_config().PROFILER_QUERY_COUNTER_THRESHOLD:
            # no need to log
            return
        try:
            for log in self.stack.logs():
                self.query_count_logger_adapter.warning(
                    f'Too many DB query for counter {self.name}', extra=log)
        except:
            logger.error('DB query counter error occurred.', exc_info=True)
