"""Microphone audio capture interface types.

Corresponds to :c:type:`retro_microphone_interface` in ``libretro.h``.
Allows cores to capture audio input from the host device.

.. seealso:: :mod:`libretro.drivers.microphone`
"""

from ctypes import Structure, c_bool, c_int, c_int16, c_size_t, c_uint, c_uint64
from dataclasses import dataclass

from libretro.ctypes import CBoolArg, CIntArg, TypedFunctionPointer, TypedPointer

RETRO_MICROPHONE_INTERFACE_VERSION = 1
"""The current version of the microphone interface."""

INTERFACE_VERSION = RETRO_MICROPHONE_INTERFACE_VERSION
"""Alias for :const:`RETRO_MICROPHONE_INTERFACE_VERSION`."""


@dataclass(init=False, slots=True)
class retro_microphone(Structure):
    """Opaque handle for an open microphone.

    Corresponds to :c:type:`retro_microphone` in ``libretro.h``.

    .. note::

        Unlike most other :mod:`ctypes`-wrapped ``struct``s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.MicrophoneDriver` implementations.

        :class:`.Core`\\s should treat instances of this class as opaque handles
        and _not_ access or modify its fields directly.
    """

    id: int
    """Opaque identifier for this microphone handle."""

    _fields_ = (("id", c_uint64),)


@dataclass(init=False, slots=True)
class retro_microphone_params(Structure):
    """Parameters for opening a microphone.

    Corresponds to :c:type:`retro_microphone_params` in ``libretro.h``.

    >>> from libretro.api.microphone import retro_microphone_params
    >>> p = retro_microphone_params()
    >>> p.rate
    0
    """

    rate: int
    """Requested sample rate in Hz."""

    _fields_ = (("rate", c_uint),)

    def __deepcopy__(self, _):
        """Returns a shallow copy.

        >>> import copy
        >>> from libretro.api.microphone import retro_microphone_params
        >>> copy.deepcopy(retro_microphone_params()).rate
        0
        """
        return retro_microphone_params(self.rate)


retro_open_mic_t = TypedFunctionPointer[
    TypedPointer[retro_microphone], [TypedPointer[retro_microphone_params]]
]
"""Opens a microphone with the given parameters."""

retro_close_mic_t = TypedFunctionPointer[None, [TypedPointer[retro_microphone]]]
"""Closes an open microphone."""

retro_get_mic_params_t = TypedFunctionPointer[
    c_bool, [TypedPointer[retro_microphone], TypedPointer[retro_microphone_params]]
]
"""Retrieves the effective parameters of an open microphone."""

retro_set_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone], CBoolArg]]
"""Enables or disables an open microphone."""

retro_get_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone]]]
"""Returns whether an open microphone is currently enabled."""

retro_read_mic_t = TypedFunctionPointer[
    c_int, [TypedPointer[retro_microphone], TypedPointer[c_int16], CIntArg[c_size_t]]
]
"""Reads audio samples from an open microphone."""


@dataclass(init=False, slots=True)
class retro_microphone_interface(Structure):
    """Corresponds to :c:type:`retro_microphone_interface` in ``libretro.h``.

    Provides functions for managing microphone input.

    >>> from libretro.api.microphone import retro_microphone_interface, INTERFACE_VERSION
    >>> mic = retro_microphone_interface(INTERFACE_VERSION)
    >>> mic.open_mic is None
    True
    """

    interface_version: int
    """Version of the microphone interface."""
    open_mic: retro_open_mic_t | None
    """Opens a microphone with the given parameters."""
    close_mic: retro_close_mic_t | None
    """Closes an open microphone."""
    get_params: retro_get_mic_params_t | None
    """Retrieves the effective parameters of an open microphone."""
    set_mic_state: retro_set_mic_state_t | None
    """Enables or disables an open microphone."""
    get_mic_state: retro_get_mic_state_t | None
    """Returns whether an open microphone is currently enabled."""
    read_mic: retro_read_mic_t | None
    """Reads audio samples from an open microphone."""

    _fields_ = (
        ("interface_version", c_uint),
        ("open_mic", retro_open_mic_t),
        ("close_mic", retro_close_mic_t),
        ("get_params", retro_get_mic_params_t),
        ("set_mic_state", retro_set_mic_state_t),
        ("get_mic_state", retro_get_mic_state_t),
        ("read_mic", retro_read_mic_t),
    )

    def __init__(
        self,
        interface_version: int,
        open_mic: retro_open_mic_t | None = None,
        close_mic: retro_close_mic_t | None = None,
        get_params: retro_get_mic_params_t | None = None,
        set_mic_state: retro_set_mic_state_t | None = None,
        get_mic_state: retro_get_mic_state_t | None = None,
        read_mic: retro_read_mic_t | None = None,
    ):
        """Initializes the interface with a required version number.

        :param interface_version: Must match :const:`INTERFACE_VERSION`.
        """
        super().__init__(
            interface_version,
            open_mic,
            close_mic,
            get_params,
            set_mic_state,
            get_mic_state,
            read_mic,
        )

    def __deepcopy__(self, _):
        """Returns a shallow copy.

        >>> import copy
        >>> from libretro.api.microphone import retro_microphone_interface, INTERFACE_VERSION
        >>> copy.deepcopy(retro_microphone_interface(INTERFACE_VERSION)).open_mic is None
        True
        """
        return retro_microphone_interface(
            self.interface_version,
            self.open_mic,
            self.close_mic,
            self.get_params,
            self.set_mic_state,
            self.get_mic_state,
            self.read_mic,
        )


__all__ = [
    "INTERFACE_VERSION",
    "retro_microphone",
    "retro_microphone_params",
    "retro_open_mic_t",
    "retro_close_mic_t",
    "retro_get_mic_params_t",
    "retro_set_mic_state_t",
    "retro_get_mic_state_t",
    "retro_read_mic_t",
    "retro_microphone_interface",
]
