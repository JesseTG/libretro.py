"""
Audio callback and sample rendering types.

Corresponds to :c:type:`retro_audio_callback` and related types in ``libretro.h``.
These types allow cores to push audio samples to the frontend
or to be notified of audio buffer status changes.

.. seealso::

    :class:`.AudioDriver`
        The protocol that uses these types to implement audio output support in libretro.py.

    :mod:`libretro.drivers.audio`
        libretro.py's included :class:`.AudioDriver` implementations.
"""

from ctypes import Structure, c_int16, c_size_t, c_uint
from dataclasses import dataclass

from libretro.ctypes import CBoolArg, CIntArg, TypedFunctionPointer, TypedPointer

retro_audio_sample_t = TypedFunctionPointer[None, [CIntArg[c_int16], CIntArg[c_int16]]]
"""
Called by the core to render a single stereo audio frame.

Corresponds to :c:type:`retro_audio_sample_t`.

.. seealso ::

    :meth:`.Core.set_audio_sample`
        The method that exposes this callback to cores.

    :meth:`.AudioDriver.sample`
        The method that implements this callback in libretro.py.

"""

retro_audio_sample_batch_t = TypedFunctionPointer[
    c_size_t, [TypedPointer[c_int16], CIntArg[c_size_t]]
]
"""
Called by the core to render multiple stereo audio frames at once.

The buffer should contain interleaved left/right channel samples, i.e. [L, R, L, R, ...].

Corresponds to :c:type:`retro_audio_sample_batch_t`.

.. seealso ::

    :meth:`.Core.set_audio_sample_batch`
        The method that exposes this callback to cores.

    :meth:`.AudioDriver.sample_batch`
        The method that implements this callback in libretro.py.
"""

retro_audio_callback_t = TypedFunctionPointer[None, []]
"""
Registered by the core so that libretro.py can request audio samples from it,
possibly on a separate thread.

Corresponds to :c:type:`retro_audio_callback_t`.

.. seealso ::

    :meth:`.AudioDriver.callback`
        The suggested entry point for this registered callback in libretro.py.
"""

retro_audio_set_state_callback_t = TypedFunctionPointer[None, [CBoolArg]]
"""
Registered by the core so that libretro.py
can tell it to start or stop rendering audio.

Corresponds to :c:type:`retro_audio_set_state_callback_t`.

.. seealso ::

    :meth:`.AudioDriver.set_state`
        The suggested entry point for this registered callback in libretro.py.
"""

retro_audio_buffer_status_callback_t = TypedFunctionPointer[
    None, [CBoolArg, CIntArg[c_uint], CBoolArg]
]
"""
Registered by the core so that libretro.py can inform the core
about the active :class:`.AudioDriver`'s buffer occupancy and underrun status.

Corresponds to :c:type:`retro_audio_buffer_status_callback_t`.

.. seealso ::

    :meth:`.AudioDriver.report_buffer_status`
        The suggested entry point for this registered callback in libretro.py.
"""


@dataclass(init=False, slots=True)
class retro_audio_callback(Structure):
    """
    Core-registered callbacks for asynchronous audio rendering.

    Corresponds to :c:type:`retro_audio_callback` in ``libretro.h``.
    """

    callback: retro_audio_callback_t | None
    """Called by the frontend to request audio samples from the core."""
    set_state: retro_audio_set_state_callback_t | None
    """Called by the frontend to notify the core whether audio output is active."""

    _fields_ = (
        ("callback", retro_audio_callback_t),
        ("set_state", retro_audio_set_state_callback_t),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this struct.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_audio_callback
        >>> cb = retro_audio_callback()
        >>> cb_copy = copy.deepcopy(cb)
        >>> cb_copy == cb
        True
        >>> cb_copy is cb
        False
        """
        return retro_audio_callback(callback=self.callback, set_state=self.set_state)


@dataclass(init=False, slots=True)
class retro_audio_buffer_status_callback(Structure):
    """
    Core-registered callback for audio buffer status reporting.

    Corresponds to :c:type:`retro_audio_buffer_status_callback` in ``libretro.h``.
    """

    callback: retro_audio_buffer_status_callback_t | None
    """Called to inform the core of the audio buffer's occupancy."""

    _fields_ = (("callback", retro_audio_buffer_status_callback_t),)

    def __call__(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        """
        Calls :attr:`callback` with the given parameters if non-:obj:`None`,
        otherwise  does nothing.

        :param active: Whether audio is active.
        :param occupancy: The current audio buffer occupancy.
        :param underrun_likely: Whether an underrun is likely.

        >>> from libretro.api import retro_audio_buffer_status_callback
        >>> cb = retro_audio_buffer_status_callback()
        >>> cb(True, 50, False)  # No-op since callback is None
        """
        if self.callback:
            self.callback(active, occupancy, underrun_likely)

    def __deepcopy__(self, _):
        """
        Returns a copy of this struct with the same callback.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_audio_buffer_status_callback
        >>> cb = retro_audio_buffer_status_callback()
        >>> cb_copy = copy.deepcopy(cb)
        >>> cb_copy == cb
        True
        >>> cb_copy is cb
        False
        """
        return retro_audio_buffer_status_callback(callback=self.callback)


__all__ = [
    "retro_audio_sample_t",
    "retro_audio_sample_batch_t",
    "retro_audio_callback_t",
    "retro_audio_set_state_callback_t",
    "retro_audio_buffer_status_callback_t",
    "retro_audio_callback",
    "retro_audio_buffer_status_callback",
]
