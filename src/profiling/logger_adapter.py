import logging
from typing import TYPE_CHECKING, Tuple, Any

if TYPE_CHECKING:
    logger_adapter = logging.LoggerAdapter[logging.Logger]
else:
    logger_adapter = logging.LoggerAdapter


class ProfilingLoggerAdapter(logger_adapter):
    def process(self, msg: str, kwargs: Any) -> Tuple[str, Any]:
        if "extra" in kwargs:
            kwargs["extra"] = {**self.extra, **kwargs["extra"]}
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs
