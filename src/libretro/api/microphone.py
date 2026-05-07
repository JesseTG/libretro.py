"""
Microphone audio capture interface types.

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
    r"""
    Opaque handle for an open microphone.

    Corresponds to :c:type:`retro_microphone` in ``libretro.h``.

    .. note::

        Unlike most other :mod:`ctypes`-wrapped ``struct``s in libretro.py,
        the fields in this class are not part of libretro.h.
        They are provided as a convenience for :class:`.MicrophoneDriver` implementations.

        :class:`.Core`\s should treat instances of this class as opaque handles
        and _not_ access or modify its fields directly.
    """

    id: int
    """Opaque identifier for this microphone handle."""

    _fields_ = (("id", c_uint64),)


@dataclass(init=False, slots=True)
class retro_microphone_params(Structure):
    """
    Parameters for opening a microphone.

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
        """
        Return a shallow copy.

        >>> import copy
        >>> from libretro.api.microphone import retro_microphone_params
        >>> copy.deepcopy(retro_microphone_params()).rate
        0
        """
        return retro_microphone_params(self.rate)


retro_open_mic_t = TypedFunctionPointer[
    TypedPointer[retro_microphone], [TypedPointer[retro_microphone_params]]
]
"""
Open a new microphone for capture.

Registered by the :term:`frontend` and called by the :term:`core`.

:param params: Pointer to a :class:`retro_microphone_params` describing the desired configuration,
    or :obj:`None` to use the frontend's defaults.
:return: A :class:`.c_void_ptr` to a :class:`retro_microphone` handle on success,
    or :obj:`None` if a microphone could not be opened.

.. note::
    Microphones are inactive by default;
    a returned handle must be enabled with :c:type:`retro_set_mic_state_t`
    before it will yield samples.

Corresponds to :c:type:`retro_open_mic_t` in ``libretro.h``.
"""

retro_close_mic_t = TypedFunctionPointer[None, [TypedPointer[retro_microphone]]]
"""
Close an open microphone and release its resources.

Registered by the :term:`frontend` and called by the :term:`core`.
After this returns, the handle must not be used again.

:param microphone: Pointer to the :class:`retro_microphone` handle to close.
    If :obj:`None`, this function does nothing.

Corresponds to :c:type:`retro_close_mic_t` in ``libretro.h``.
"""

retro_get_mic_params_t = TypedFunctionPointer[
    c_bool, [TypedPointer[retro_microphone], TypedPointer[retro_microphone_params]]
]
"""
Retrieve the configured parameters of an open microphone.

Registered by the :term:`frontend` and called by the :term:`core`.
The returned parameters may differ from those originally requested
depending on driver and device support.

:param microphone: Pointer to the :class:`retro_microphone` whose parameters will be queried.
:param params: Pointer to a :class:`retro_microphone_params` that will be filled in.
:return: :obj:`True` on success, :obj:`False` if either argument is invalid.

Corresponds to :c:type:`retro_get_mic_params_t` in ``libretro.h``.
"""

retro_set_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone], CBoolArg]]
"""
Enable or disable an open microphone.

Registered by the :term:`frontend` and called by the :term:`core`.
A disabled microphone will not produce samples
and has minimal performance impact.

:param microphone: Pointer to the :class:`retro_microphone` whose state will change.
:param state: :obj:`True` to enable the microphone, :obj:`False` to pause it.
:return: :obj:`True` if the state was successfully set,
    :obj:`False` if ``microphone`` is invalid or there was an error.

Corresponds to :c:type:`retro_set_mic_state_t` in ``libretro.h``.
"""

retro_get_mic_state_t = TypedFunctionPointer[c_bool, [TypedPointer[retro_microphone]]]
"""
Return whether an open microphone is currently enabled.

Registered by the :term:`frontend` and called by the :term:`core`.

:param microphone: Pointer to the :class:`retro_microphone` to query.
:return: :obj:`True` if ``microphone`` is valid and active, :obj:`False` otherwise.

Corresponds to :c:type:`retro_get_mic_state_t` in ``libretro.h``.
"""

retro_read_mic_t = TypedFunctionPointer[
    c_int, [TypedPointer[retro_microphone], TypedPointer[c_int16], CIntArg[c_size_t]]
]
"""
Read captured audio samples from an open microphone.

Registered by the :term:`frontend` and called by the :term:`core`,
which must do so every frame while the microphone is enabled.

:param microphone: Pointer to the :class:`retro_microphone` to read from.
:param samples: Pointer to a buffer of signed 16-bit mono samples that will be filled.
:param num_samples: Capacity of ``samples``, in samples (not bytes).
:return: The number of samples actually written to ``samples``,
    or ``-1`` if the microphone is disabled,
    the audio driver is paused,
    or there was an error.

Corresponds to :c:type:`retro_read_mic_t` in ``libretro.h``.
"""


@dataclass(init=False, slots=True)
class retro_microphone_interface(Structure):
    """
    Corresponds to :c:type:`retro_microphone_interface` in ``libretro.h``.

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
        """
        Initialize the interface with a required version number.

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
        """
        Return a shallow copy.

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
