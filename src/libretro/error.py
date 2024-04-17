class UnsupportedEnvCall(Exception):
    def __init__(self, message):
        super().__init__(message)


class CoreShutDownException(Exception):
    def __init__(self, *args):
        super().__init__("Core has been shut down", *args)


__all__ = [
    "UnsupportedEnvCall",
    "CoreShutDownException",
]
