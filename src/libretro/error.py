"""Exception types raised by libretro.py's drivers and core wrapper."""

from collections.abc import Sequence


class UnsupportedEnvCall(Exception):
    """Raised by a driver to signal that it does not support an environment call."""

    def __init__(self, message: str, *args: object):
        """Construct the exception with a human-readable ``message``."""
        super().__init__(message, *args)


class CoreShutDownException(Exception):
    """Raised when an operation is attempted on a core that has been shut down."""

    def __init__(self, *args: object):
        """Construct the exception with the standard shutdown message."""
        super().__init__("Core has been shut down", *args)


class CallbackException(RuntimeError):
    """Wraps an exception raised inside a callback invoked by the core."""

    def __init__(self, message: str, *args: object):
        """Construct the wrapper with a human-readable ``message``."""
        super().__init__(message, *args)


class CallbackExceptionGroup(ExceptionGroup):
    """Aggregates multiple :class:`CallbackException` instances raised within one frame."""

    def __init__(self, message: str, exceptions: Sequence[Exception]):
        """Construct the group with a human-readable ``message`` and the wrapped ``exceptions``."""
        super().__init__(message, exceptions)

    def __new__(cls, message: str, exceptions: Sequence[Exception]):
        """Construct the group via :class:`ExceptionGroup`'s ``__new__`` (required for subclassing)."""
        return super().__new__(cls, message, exceptions)


__all__ = [
    "UnsupportedEnvCall",
    "CoreShutDownException",
    "CallbackException",
    "CallbackExceptionGroup",
]
