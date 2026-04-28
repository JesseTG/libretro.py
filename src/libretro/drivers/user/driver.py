"""
Protocol definition for the user driver interface.

.. seealso::

    :mod:`libretro.api.user`
        Provides the language and username types that :class:`.UserDriver` implementations supply.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.user import Language


@runtime_checkable
class UserDriver(Protocol):
    """
    Protocol for drivers that supply player identity information to the core.

    Cores query this information via ``RETRO_ENVIRONMENT_GET_USERNAME``
    and ``RETRO_ENVIRONMENT_GET_LANGUAGE``.

    .. seealso::

        :mod:`libretro.api.user`
            The language enumeration and username types that implementations of this protocol supply.
    """

    @property
    @abstractmethod
    def username(self) -> bytes | None:
        """
        The player username exposed to the core via ``RETRO_ENVIRONMENT_GET_USERNAME``.

        :obj:`None` disables the environment call.
        """
        ...

    @property
    @abstractmethod
    def language(self) -> Language | None:
        """
        The UI language exposed to the core via ``RETRO_ENVIRONMENT_GET_LANGUAGE``.

        :obj:`None` disables the environment call.
        """
        ...


__all__ = ["UserDriver"]
