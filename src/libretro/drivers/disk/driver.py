"""
:class:`~typing.Protocol` definition for the emulated disk-control interface.

.. seealso::

    :mod:`libretro.api.disk`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api.disk import (
    retro_disk_control_callback,
    retro_disk_control_ext_callback,
)


@runtime_checkable
class DiskDriver(Protocol):
    """
    Protocol for drivers that expose the emulated system's disk-control interface.

    .. seealso::

        :mod:`libretro.api.disk`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def version(self) -> int:
        """
        The version of the disk-control interface registered by the core.

        Returns ``1`` if the core registered a :class:`.retro_disk_control_callback`
        via ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE``,
        ``2`` if it registered a :class:`.retro_disk_control_ext_callback`
        via ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE``,
        and ``0`` if no callback has been registered.
        """
        ...

    @property
    @abstractmethod
    def callback(
        self,
    ) -> retro_disk_control_callback | retro_disk_control_ext_callback | None:
        """
        The disk-control callback registered by the core, if any.

        The concrete type reflects which env-call the core used to register it.
        :obj:`None` if the core has not registered a disk-control interface.

        :param value: The callback to register.
            Use :class:`.retro_disk_control_callback` for v1
            and :class:`.retro_disk_control_ext_callback` for v2.
        :raises UnsupportedEnvCall: If this driver does not accept disk-control callbacks
            of the given type.

        .. seealso::

            :class:`~libretro.api.disk.retro_disk_control_callback`
                The v1 callback struct registered via ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_INTERFACE``.

            :class:`~libretro.api.disk.retro_disk_control_ext_callback`
                The v2 callback struct registered via ``RETRO_ENVIRONMENT_SET_DISK_CONTROL_EXT_INTERFACE``.
        """
        ...

    @callback.setter
    @abstractmethod
    def callback(
        self, value: retro_disk_control_callback | retro_disk_control_ext_callback
    ) -> None:
        """See :attr:`callback`."""
        ...

    @callback.deleter
    @abstractmethod
    def callback(self) -> None:
        """See :attr:`callback`."""
        ...

    @property
    @abstractmethod
    def eject_state(self) -> bool:
        """
        Whether the emulated disk tray is currently open.

        Reads and writes pass through to
        :attr:`.retro_disk_control_callback.get_eject_state`
        and :attr:`.retro_disk_control_callback.set_eject_state` respectively.

        :param value: :obj:`True` to open the tray, :obj:`False` to close it.
        :raises UnsupportedEnvCall: If no disk-control callback has been registered.
        """
        ...

    @eject_state.setter
    @abstractmethod
    def eject_state(self, value: bool) -> None:
        """See :attr:`eject_state`."""
        ...


__all__ = [
    "DiskDriver",
]
