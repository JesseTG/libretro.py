class UnsupportedEnvCall(Exception):
    def __init__(self, message: str, *args: object):
        super().__init__(message, *args)


class CoreShutDownException(Exception):
    def __init__(self, *args: object):
        super().__init__("Core has been shut down", *args)


__all__ = [
    "UnsupportedEnvCall",
    "CoreShutDownException",
]
