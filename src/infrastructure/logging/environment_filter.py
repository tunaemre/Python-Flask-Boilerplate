from logging import Filter, LogRecord


class EnvironmentFilter(Filter):

    def __init__(self, environment: str):
        super().__init__()
        self.environment = environment

    def filter(self, record: LogRecord) -> bool:
        record.environment = self.environment
        return True
