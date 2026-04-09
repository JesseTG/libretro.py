from collections.abc import Sequence


class UnsupportedEnvCall(Exception):
    def __init__(self, message: str, *args: object):
        super().__init__(message, *args)


class CoreShutDownException(Exception):
    def __init__(self, *args: object):
        super().__init__("Core has been shut down", *args)


class CallbackException(RuntimeError):
    def __init__(self, message: str, *args: object):
        super().__init__(message, *args)


class CallbackExceptionGroup(ExceptionGroup):
    def __init__(self, message: str, exceptions: Sequence[Exception], *args: object):
        super().__init__(message, exceptions)
        self.args = args

    def __new__(cls, message: str, exceptions: Sequence[Exception], *args: object):
        return super().__new__(cls, message, exceptions)


__all__ = [
    "UnsupportedEnvCall",
    "CoreShutDownException",
    "CallbackException",
    "CallbackExceptionGroup",
]
