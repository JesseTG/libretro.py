"""
Types for managing the rate at which the :class:`.Core` runs.

.. seealso:: :mod:`libretro.drivers.timing`
"""

from ctypes import Structure, c_bool, c_float, c_int64, c_uint
from dataclasses import dataclass
from enum import IntEnum

RETRO_THROTTLE_NONE = 0
RETRO_THROTTLE_FRAME_STEPPING = 1
RETRO_THROTTLE_FAST_FORWARD = 2
RETRO_THROTTLE_SLOW_MOTION = 3
RETRO_THROTTLE_REWINDING = 4
RETRO_THROTTLE_VSYNC = 5
RETRO_THROTTLE_UNBLOCKED = 6


retro_usec_t = c_int64
"""A timestamp or duration in microseconds."""

from libretro.ctypes import CIntArg, TypedFunctionPointer

retro_frame_time_callback_t = TypedFunctionPointer[None, [CIntArg[retro_usec_t]]]
"""Called each frame with the elapsed time in microseconds."""


@dataclass(init=False, slots=True)
class retro_frame_time_callback(Structure):
    """Corresponds to :c:type:`retro_frame_time_callback` in ``libretro.h``.

    Wraps a callback that is invoked each frame with the elapsed time.

    >>> from libretro.api import retro_frame_time_callback
    >>> cb = retro_frame_time_callback()
    >>> cb.reference
    0
    """

    callback: retro_frame_time_callback_t | None
    """Called each frame with the elapsed time in microseconds."""
    reference: int
    """Ideal duration of one frame in microseconds."""

    _fields_ = (
        ("callback", retro_frame_time_callback_t),
        ("reference", c_uint),
    )

    def __call__(self, time: CIntArg[retro_usec_t] | None = None):
        """
        Invokes :attr:`callback` with the given time, or with :attr:`reference` if it's :obj:`None`.

        Does nothing if :attr:`callback` is unset.
        """

        if self.callback:
            if time is None:
                self.callback(self.reference)
            else:
                self.callback(time)

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_frame_time_callback
        >>> copy.deepcopy(retro_frame_time_callback()).reference
        0
        """
        return retro_frame_time_callback(self.callback, self.reference)


class ThrottleMode(IntEnum):
    """The frontend's current throttle mode.

    >>> from libretro.api import ThrottleMode
    >>> ThrottleMode.FAST_FORWARD
    <ThrottleMode.FAST_FORWARD: 2>
    """

    NONE = RETRO_THROTTLE_NONE
    FRAME_STEPPING = RETRO_THROTTLE_FRAME_STEPPING
    FAST_FORWARD = RETRO_THROTTLE_FAST_FORWARD
    SLOW_MOTION = RETRO_THROTTLE_SLOW_MOTION
    REWINDING = RETRO_THROTTLE_REWINDING
    VSYNC = RETRO_THROTTLE_VSYNC
    UNBLOCKED = RETRO_THROTTLE_UNBLOCKED


@dataclass(init=False, slots=True)
class retro_fastforwarding_override(Structure):
    """
    Allows the core to take control over fast-forwarding behavior.

    Corresponds to :c:type:`retro_fastforwarding_override` in ``libretro.h``.

    >>> from libretro.api import retro_fastforwarding_override
    >>> ff = retro_fastforwarding_override()
    >>> ff.fastforward
    False
    """

    ratio: float
    """Maximum fast-forward ratio. ``0.0`` for no limit."""
    fastforward: bool
    """Whether the frontend should fast-forward."""
    notification: bool
    """Whether the frontend should display a fast-forward notification."""
    inhibit_toggle: bool
    """Whether the player should be prevented from toggling fast-forward."""

    _fields_ = (
        ("ratio", c_float),
        ("fastforward", c_bool),
        ("notification", c_bool),
        ("inhibit_toggle", c_bool),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_fastforwarding_override
        >>> copy.deepcopy(retro_fastforwarding_override()).fastforward
        False
        """
        return retro_fastforwarding_override(
            self.ratio, self.fastforward, self.notification, self.inhibit_toggle
        )


@dataclass(init=False, slots=True)
class retro_throttle_state(Structure):
    """
    Reports the frontend's current throttle mode and rate.

    Corresponds to :c:type:`retro_throttle_state` in ``libretro.h``.

    >>> from libretro.api import retro_throttle_state
    >>> ts = retro_throttle_state()
    >>> ts.rate
    0.0
    """

    mode: ThrottleMode
    """Current throttle mode."""
    rate: float
    """Rate at which the frontend is trying to run, as a multiple of normal speed."""

    _fields_ = (
        ("mode", c_uint),
        ("rate", c_float),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_throttle_state
        >>> copy.deepcopy(retro_throttle_state()).rate
        0.0
        """
        return retro_throttle_state(self.mode, self.rate)


__all__ = [
    "ThrottleMode",
    "retro_fastforwarding_override",
    "retro_throttle_state",
    "retro_frame_time_callback",
    "retro_usec_t",
    "retro_frame_time_callback_t",
]
