"""Geographic location service interface types.

Allows cores to access the host device's geographic location.

.. seealso:: :mod:`libretro.drivers.location`
"""

from ctypes import Structure, c_bool, c_double, c_uint
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

retro_location_set_interval_t = TypedFunctionPointer[None, [CIntArg[c_uint], CIntArg[c_uint]]]
"""Sets the location polling interval and distance threshold."""

retro_location_start_t = TypedFunctionPointer[c_bool, []]
"""Starts location services. Returns :obj:`True` on success."""

retro_location_stop_t = TypedFunctionPointer[None, []]
"""Stops location services."""

retro_location_get_position_t = TypedFunctionPointer[
    c_bool,
    [
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
    ],
]
"""Retrieves the current geographic position (lat, lon, horiz accuracy, vert accuracy)."""

retro_location_lifetime_status_t = TypedFunctionPointer[None, []]
"""Called when location services are initialized or deinitialized."""


@dataclass(init=False, slots=True)
class retro_location_callback(Structure):
    """Corresponds to :c:type:`retro_location_callback` in ``libretro.h``.

    A set of callbacks for managing location services.

    >>> from libretro.api import retro_location_callback
    >>> loc = retro_location_callback()
    >>> loc.start is None
    True
    """

    start: retro_location_start_t | None
    """Starts the location service. Set by the frontend."""
    stop: retro_location_stop_t | None
    """Stops the location service. Set by the frontend."""
    get_position: retro_location_get_position_t | None
    """Returns the device's current geographic coordinates. Set by the frontend."""
    set_interval: retro_location_set_interval_t | None
    """Sets the location update interval. Set by the frontend."""
    initialized: retro_location_lifetime_status_t | None
    """Called when the location service is initialized. Set by the core. Optional."""
    deinitialized: retro_location_lifetime_status_t | None
    """Called when the location service is deinitialized. Set by the core. Optional."""

    _fields_ = (
        ("start", retro_location_start_t),
        ("stop", retro_location_stop_t),
        ("get_position", retro_location_get_position_t),
        ("set_interval", retro_location_set_interval_t),
        ("initialized", retro_location_lifetime_status_t),
        ("deinitialized", retro_location_lifetime_status_t),
    )

    def __deepcopy__(self, _):
        """
        Returns a deep copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_location_callback
        >>> copy.deepcopy(retro_location_callback()).start is None
        True
        """
        return retro_location_callback(
            self.start,
            self.stop,
            self.get_position,
            self.set_interval,
            self.initialized,
            self.deinitialized,
        )


__all__ = [
    "retro_location_callback",
    "retro_location_get_position_t",
    "retro_location_lifetime_status_t",
    "retro_location_set_interval_t",
    "retro_location_start_t",
    "retro_location_stop_t",
]
