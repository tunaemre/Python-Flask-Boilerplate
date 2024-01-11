import logging
import time
from typing import Any, Dict, Optional, List, Callable
from uuid import uuid4

from src.config import get_environment, app_config_manager
from src.profiling.logger_adapter import ProfilingLoggerAdapter

logger = logging.getLogger(__name__)


class _MockTimerContext:
    def __enter__(self) -> None:
        pass

    def __exit__(self, *args: Any) -> None:
        pass


class _RequestTimerContext:
    def __init__(self, key: str, opened: Callable[..., int], closed: Callable[..., None], **kwargs: Any) -> None:
        self.key = key
        self.opened = opened
        self.closed = closed
        self.kwargs = kwargs
        self.start_time = 0.0
        self.end_time = 0.0
        self.context_index = 0

    def open(self) -> None:
        if self.start_time == 0:
            self.start_time = time.time()
            self.context_index = self.opened()

    def close(self) -> None:
        if self.end_time == 0:
            self.end_time = time.time()
            self.closed()

    def __enter__(self) -> None:
        self.open()

    def __exit__(self, *args: Any) -> None:
        self.close()

    @property
    def is_closed(self) -> bool:
        return self.start_time > 0 and self.end_time > 0

    @property
    def context_time(self) -> float:
        return self.end_time - self.start_time


class _RequestTimerStack:
    def __init__(self) -> None:
        self.keys: List[str] = []
        self.items: List[_RequestTimerContext] = []

    def append(self, item: _RequestTimerContext) -> None:
        self.keys.append(item.key)
        self.items.append(item)

    def index(self, key: str) -> int:
        try:
            return self.keys.index(key)
        except ValueError:
            return -1

    def close(self) -> None:
        for s in reversed(self.items):
            if not s.is_closed:
                s.close()

    def logs(self) -> List[Dict[str, Any]]:
        max_profile_time = float('-inf')
        max_profile_index = -1
        items: List[Dict[str, Any]] = []
        profile_total_time = self.total  # profile total time (time of n stack)
        total_time = profile_total_time
        while stack_item := self.pop():
            new_total_time = self.total  # new total is inner total times (time of n-1 stack)
            profile_time = total_time - new_total_time
            if profile_time > max_profile_time:
                max_profile_time = profile_time
                max_profile_index = len(items)
            items.append(
                {
                    'profile_total_time': profile_total_time,
                    'profile_time': profile_time,
                    'profile_function_name': stack_item.key,
                    'profile_start_time': stack_item.start_time,
                    **stack_item.kwargs
                }
            )
            total_time = new_total_time  # new total is inner total times (time of n-1 stack)
        if max_profile_index > -1:
            items[max_profile_index]['profile_slowest'] = 1
        return items

    def pop(self) -> Optional[_RequestTimerContext]:
        try:
            self.keys.pop(0)
            return self.items.pop(0)
        except IndexError:
            return None

    @property
    def total(self) -> float:
        t = 0.0
        context_index = None
        for s in self.items:
            if context_index is None:
                context_index = s.context_index
            elif context_index != s.context_index:
                break
            t += s.context_time
        return t


class RequestTimer:

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.uuid = str(uuid4())
        self.stack = _RequestTimerStack()
        self.time_logger_adapter = ProfilingLoggerAdapter(
            logger,
            extra={**{'timer_log': 1,
                      'timer_uuid': self.uuid,
                      'environment': get_environment()},
                   **kwargs})
        self._context_index = 0
        self._is_closed = False

    def __call__(self, key: str, **kwargs: Any) -> _RequestTimerContext:
        context = _RequestTimerContext(
            key=key,
            opened=self._opened,
            closed=self._closed,
            **kwargs
        )
        self.stack.append(context)
        return context

    def _opened(self) -> int:
        self._context_index += 1
        return self._context_index

    def _closed(self) -> None:
        self._context_index -= 1

    def try_to_close(self, key: str, on_close: Optional[Callable[..., None]] = None) -> None:
        index = self.stack.index(key)
        if index == 0:
            self._close()
            if on_close is not None:
                on_close()

    def force_close(self) -> None:
        self._close()

    def _close(self) -> None:
        if self._is_closed:
            return
        self._is_closed = True
        # finalize request timer
        self.stack.close()
        total = self.stack.total
        if total < app_config_manager.get_config().PROFILER_REQUEST_TIMER_THRESHOLD:
            # no need to log
            return
        try:
            for log in self.stack.logs():
                self.time_logger_adapter.warning(f'High response time for timer {self.name}',
                                                 extra=log)
        except:
            logger.error('Request timer error occurred.', exc_info=True)
