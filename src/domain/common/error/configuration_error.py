class ConfigurationError(Exception):
    def __init__(self, message: str, error_code: str) -> None:
        super().__init__(message, error_code)
