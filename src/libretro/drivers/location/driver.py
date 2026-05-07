"""
:class:`~typing.Protocol` definition for geolocation drivers.

.. seealso::

    :mod:`libretro.api.location`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from libretro.api.location import retro_location_lifetime_status_t


@dataclass(frozen=True, slots=True)
class Position:
    """A geographic position reported by a :class:`LocationDriver`."""

    latitude: float | None
    longitude: float | None
    horizontal_accuracy: float | None
    vertical_accuracy: float | None


@runtime_checkable
class LocationDriver(Protocol):
    """
    Protocol for drivers that supply geographic position updates to a core.

    .. seealso::

        :mod:`libretro.api.location`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @abstractmethod
    def start(self) -> bool:
        """
        Begin reporting geographic position updates to the core.

        Called by the core through :attr:`.retro_location_callback.start`.

        :return: :obj:`True` if the location service started successfully.

        .. seealso::

            :data:`~libretro.api.location.retro_location_start_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """
        Stop reporting geographic position updates to the core.

        Called by the core through :attr:`.retro_location_callback.stop`.

        .. seealso::

            :data:`~libretro.api.location.retro_location_stop_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def get_position(self) -> Position | None:
        """
        Return the most recently observed geographic position.

        :return: The latest :class:`Position`, or :obj:`None` if no fix is available yet.

        .. seealso::

            :data:`~libretro.api.location.retro_location_get_position_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def set_interval(self, interval: int, distance: int) -> None:
        """
        Configure how frequently the driver should produce position updates.

        :param interval: Minimum time between updates in milliseconds.
        :param distance: Minimum distance between updates in meters.

        .. seealso::

            :data:`~libretro.api.location.retro_location_set_interval_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @property
    @abstractmethod
    def initialized(self) -> retro_location_lifetime_status_t | None:
        """
        Callback the driver invokes after it finishes initializing.

        Registered by the core through :attr:`.retro_location_callback.initialized`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke after initialization,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.location.retro_location_lifetime_status_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @initialized.setter
    @abstractmethod
    def initialized(self, value: retro_location_lifetime_status_t | None) -> None:
        """See :attr:`initialized`."""
        ...

    @property
    @abstractmethod
    def deinitialized(self) -> retro_location_lifetime_status_t | None:
        """
        Callback the driver invokes immediately before it deinitializes.

        Registered by the core through :attr:`.retro_location_callback.deinitialized`;
        :obj:`None` if the core has not registered one.

        :param value: The callback to invoke before deinitialization,
            or :obj:`None` to clear it.

        .. seealso::

            :data:`~libretro.api.location.retro_location_lifetime_status_t`
                The C function pointer type that this attribute holds.
        """
        ...

    @deinitialized.setter
    @abstractmethod
    def deinitialized(self, value: retro_location_lifetime_status_t | None) -> None:
        """See :attr:`deinitialized`."""
        ...


__all__ = [
    "LocationDriver",
    "Position",
]
