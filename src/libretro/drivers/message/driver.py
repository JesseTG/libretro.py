"""
Protocol definition for the message driver interface.

.. seealso::

    :mod:`libretro.api.message`
        Provides the message types that :class:`.MessageDriver` implementations display or log.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api import retro_message, retro_message_ext


@runtime_checkable
class MessageDriver(Protocol):
    """
    Protocol for drivers that handle on-screen or logged messages sent by the core.

    Cores deliver messages via ``RETRO_ENVIRONMENT_SET_MESSAGE``
    or ``RETRO_ENVIRONMENT_SET_MESSAGE_EXT``.

    .. seealso::

        :mod:`libretro.api.message`
            The message types delivered to implementations of this protocol.
    """

    @property
    @abstractmethod
    def version(self) -> int:
        """
        The message-interface version supported by this driver.

        ``0`` supports only :class:`~libretro.api.message.retro_message`.
        ``1`` additionally supports :class:`~libretro.api.message.retro_message_ext`.
        """
        ...

    @abstractmethod
    def set_message(self, message: retro_message | retro_message_ext | None) -> bool:
        """
        Delivers a message from the core.

        Corresponds to the ``RETRO_ENVIRONMENT_SET_MESSAGE`` and
        ``RETRO_ENVIRONMENT_SET_MESSAGE_EXT`` environment calls.

        :param message: The message to display or log, or :obj:`None`.
        :return: :obj:`True` if the message was accepted.

        .. seealso::

            :class:`~libretro.api.message.retro_message`
                The legacy message struct delivered via ``RETRO_ENVIRONMENT_SET_MESSAGE``.

            :class:`~libretro.api.message.retro_message_ext`
                The extended message struct delivered via ``RETRO_ENVIRONMENT_SET_MESSAGE_EXT``.
        """
        ...


__all__ = [
    "MessageDriver",
]
