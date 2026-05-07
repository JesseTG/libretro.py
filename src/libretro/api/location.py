"""
Geographic location service interface types.

Allows cores to access the host device's geographic location.

.. seealso:: :mod:`libretro.drivers.location`
"""

from ctypes import Structure, c_bool, c_double, c_uint
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

retro_location_set_interval_t = TypedFunctionPointer[None, [CIntArg[c_uint], CIntArg[c_uint]]]
"""
Set the desired update rate for the location service.

Registered by the :term:`frontend` and called by the :term:`core`
to hint how often it would like new location updates.
Some platforms may honor only one of the two parameters.

:param interval_ms: Desired period between updates, in milliseconds.
:param interval_distance: Desired distance between updates, in meters.

Corresponds to :c:type:`retro_location_set_interval_t` in ``libretro.h``.
"""

retro_location_start_t = TypedFunctionPointer[c_bool, []]
"""
Start listening to the host device's location service.

Registered by the :term:`frontend` and called by the :term:`core`.

:return: :obj:`True` if location services were successfully started,
    :obj:`False` if they are unavailable or the frontend lacks permission.

Corresponds to :c:type:`retro_location_start_t` in ``libretro.h``.
"""

retro_location_stop_t = TypedFunctionPointer[None, []]
"""
Stop listening to the host device's location service.

Registered by the :term:`frontend` and called by the :term:`core`.

Corresponds to :c:type:`retro_location_stop_t` in ``libretro.h``.
"""

retro_location_get_position_t = TypedFunctionPointer[
    c_bool,
    [
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
        TypedPointer[c_double],
    ],
]
"""
Return the device's most recent geographic position.

Registered by the :term:`frontend` and called by the :term:`core`.
Each output parameter is set to ``0.0`` if no change has occurred
since the last call.

:param lat: Pointer to a :class:`~ctypes.c_double` that receives the latitude, in degrees.
:param lon: Pointer to a :class:`~ctypes.c_double` that receives the longitude, in degrees.
:param horiz_accuracy: Pointer to a :class:`~ctypes.c_double` that receives the horizontal accuracy.
:param vert_accuracy: Pointer to a :class:`~ctypes.c_double` that receives the vertical accuracy.
:return: :obj:`True` on success.

Corresponds to :c:type:`retro_location_get_position_t` in ``libretro.h``.
"""

retro_location_lifetime_status_t = TypedFunctionPointer[None, []]
"""
Notify the core that the location service has been initialized or deinitialized.

Registered by the :term:`core` and called by the :term:`frontend`
when the location service starts or stops.

Corresponds to :c:type:`retro_location_lifetime_status_t` in ``libretro.h``.
"""


@dataclass(init=False, slots=True)
class retro_location_callback(Structure):
    """
    Corresponds to :c:type:`retro_location_callback` in ``libretro.h``.

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
        Return a deep copy of this object.
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
