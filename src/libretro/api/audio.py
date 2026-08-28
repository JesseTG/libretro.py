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

from ctypes import Structure, c_float, c_int16, c_size_t, c_uint
from dataclasses import dataclass

from libretro.api._utils import NullPointerToNoneMixin
from libretro.ctypes import CBoolArg, CIntArg, TypedFunctionPointer, TypedPointer

retro_audio_sample_t = TypedFunctionPointer[None, [CIntArg[c_int16], CIntArg[c_int16]]]
"""
Render a single stereo audio frame.

Called by the :term:`core` to push one signed 16-bit sample per channel to the frontend.

:param left: Signed 16-bit sample for the left channel.
:param right: Signed 16-bit sample for the right channel.

Corresponds to :c:type:`retro_audio_sample_t` in ``libretro.h``.

.. seealso::

    :meth:`.Core.set_audio_sample`
        The method that exposes this callback to cores.

    :meth:`.AudioDriver.sample`
        The method that implements this callback in libretro.py.
"""

retro_audio_sample_batch_t = TypedFunctionPointer[
    c_size_t, [TypedPointer[c_int16], CIntArg[c_size_t]]
]
"""
Render multiple stereo audio frames at once.

Called by the :term:`core` to push a buffer of interleaved
signed 16-bit left/right samples (i.e. ``[L, R, L, R, ...]``) to the frontend.

:param data: Pointer to a buffer of interleaved signed 16-bit samples.
:param frames: Number of stereo frames in ``data`` (i.e. half the number of samples).
:return: The number of frames that were processed by the frontend.

Corresponds to :c:type:`retro_audio_sample_batch_t` in ``libretro.h``.

.. seealso::

    :meth:`.Core.set_audio_sample_batch`
        The method that exposes this callback to cores.

    :meth:`.AudioDriver.sample_batch`
        The method that implements this callback in libretro.py.
"""

retro_audio_sample_batch_float_t = TypedFunctionPointer[
    c_size_t, [TypedPointer[c_float], CIntArg[c_size_t]]
]
"""
Render multiple stereo audio frames at once, in floating-point format.

The floating-point counterpart of :data:`retro_audio_sample_batch_t`,
for cores whose audio is already float-native
and would otherwise narrow it to 16 bits
only for the frontend to widen it again.

Registered by the :term:`frontend` and called by the :term:`core`,
but only after :attr:`.EnvironmentCall.GET_AUDIO_SAMPLE_BATCH_FLOAT` reports success.
A core must pick one sample format per loaded game
and must not alternate between this callback and the 16-bit ones.

:param data: Pointer to a buffer of interleaved left/right samples
    (i.e. ``[L, R, L, R, ...]``), each normalized to the range ``[-1.0, 1.0]``.
:param frames: Number of stereo frames in ``data`` (i.e. half the number of samples).
:return: The number of frames that were processed by the frontend.

Corresponds to :c:type:`retro_audio_sample_batch_float_t` in ``libretro.h``.

.. seealso::

    :data:`retro_audio_sample_batch_t`
        The 16-bit callback that cores must fall back to
        when the frontend declines to negotiate float output.
"""

retro_audio_callback_t = TypedFunctionPointer[None, []]
"""
Render audio samples on demand.

Registered by the :term:`core` and called by the :term:`frontend`
when it is ready to receive audio output;
the core should respond by pushing samples through
:c:type:`retro_audio_sample_t` or :c:type:`retro_audio_sample_batch_t`.

.. warning::
    The frontend may invoke this callback from any thread,
    so its implementation must be thread-safe.

Corresponds to :c:type:`retro_audio_callback_t` in ``libretro.h``.

.. seealso::

    :meth:`.AudioDriver.callback`
        The suggested entry point for this registered callback in libretro.py.
"""

retro_audio_set_state_callback_t = TypedFunctionPointer[None, [CBoolArg]]
"""
Notify the core that audio rendering should start or stop.

Registered by the :term:`core` and called by the :term:`frontend`
to indicate whether the audio driver is currently active.

:param enabled: :obj:`True` if the frontend's audio driver is active and ready to receive samples,
    :obj:`False` if it is paused.

Corresponds to :c:type:`retro_audio_set_state_callback_t` in ``libretro.h``.

.. seealso::

    :meth:`.AudioDriver.set_state`
        The suggested entry point for this registered callback in libretro.py.
"""

retro_audio_buffer_status_callback_t = TypedFunctionPointer[
    None, [CBoolArg, CIntArg[c_uint], CBoolArg]
]
"""
Report the frontend's audio buffer occupancy to the core.

Registered by the :term:`core` and called by the :term:`frontend`
right before each frame so the core can react to impending buffer underruns
(for example, by skipping a frame).

:param active: :obj:`True` if the frontend's audio buffer is currently in use,
    :obj:`False` if audio is disabled.
:param occupancy: Audio buffer occupancy as a percentage in the range ``[0, 100]``.
:param underrun_likely: :obj:`True` if the frontend expects an audio buffer
    underrun on the next frame.

Corresponds to :c:type:`retro_audio_buffer_status_callback_t` in ``libretro.h``.

.. seealso::

    :meth:`.AudioDriver.report_buffer_status`
        The suggested entry point for this registered callback in libretro.py.
"""


@dataclass(init=False, slots=True)
class retro_audio_callback(Structure, NullPointerToNoneMixin):
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
        Return a copy of this struct.
        Intended for use with :func:`copy.deepcopy`.

        >>> from copy import deepcopy
        >>> from ctypes import addressof
        >>> from libretro.api import retro_audio_callback
        >>> cb = retro_audio_callback()
        >>> cb_copy = deepcopy(cb)
        >>> cb is cb_copy
        False
        >>> addressof(cb) == addressof(cb_copy)
        False
        """
        return retro_audio_callback(callback=self.callback, set_state=self.set_state)


@dataclass(init=False, slots=True)
class retro_audio_sample_float_callback(Structure, NullPointerToNoneMixin):
    """
    Frontend-provided callback for pushing audio to the frontend in floating-point format.

    Corresponds to :c:type:`retro_audio_sample_float_callback` in ``libretro.h``.

    Unlike :class:`retro_audio_callback`, which the core fills in and hands to the frontend,
    the frontend populates this struct in response to
    :attr:`.EnvironmentCall.GET_AUDIO_SAMPLE_BATCH_FLOAT`.
    The core should negotiate once during :meth:`.Core.load_game`,
    and the returned pointer stays valid until :meth:`.Core.unload_game`.
    """

    batch: retro_audio_sample_batch_float_t | None
    """Called by the core to push a batch of floating-point audio frames to the frontend."""

    _fields_ = (("batch", retro_audio_sample_batch_float_t),)

    def __deepcopy__(self, _):
        """
        Return a copy of this struct.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_audio_sample_float_callback
        >>> copy.deepcopy(retro_audio_sample_float_callback()).batch is None
        True
        """
        return retro_audio_sample_float_callback(batch=self.batch)


@dataclass(init=False, slots=True)
class retro_audio_buffer_status_callback(Structure, NullPointerToNoneMixin):
    """
    Core-registered callback for audio buffer status reporting.

    Corresponds to :c:type:`retro_audio_buffer_status_callback` in ``libretro.h``.
    """

    callback: retro_audio_buffer_status_callback_t | None
    """Called to inform the core of the audio buffer's occupancy."""

    _fields_ = (("callback", retro_audio_buffer_status_callback_t),)

    def __call__(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        """
        Call :attr:`callback` with the given parameters if non-:obj:`None`,
        otherwise does nothing.

        :param active: Whether audio is active.
        :param occupancy: The current audio buffer occupancy.
        :param underrun_likely: Whether an underrun is likely.

        >>> from libretro.api import retro_audio_buffer_status_callback
        >>> cb = retro_audio_buffer_status_callback()
        >>> cb(True, 50, False) # No-op since callback is None
        >>> cb.callback(True, 50, False) # But when calling the function pointer directly...
        Traceback (most recent call last):
        TypeError: 'NoneType' object is not callable
        """
        if self.callback:
            self.callback(active, occupancy, underrun_likely)

    def __deepcopy__(self, _):
        """
        Return a copy of this struct with the same callback.
        Intended for use with :func:`copy.deepcopy`.

        >>> from copy import deepcopy
        >>> from ctypes import addressof
        >>> from libretro.api import retro_audio_buffer_status_callback
        >>> cb = retro_audio_buffer_status_callback()
        >>> cb_copy = deepcopy(cb)
        >>> cb is cb_copy # They're different Python objects
        False
        >>> addressof(cb) == addressof(cb_copy) # And they contain different C buffers
        False
        """
        return retro_audio_buffer_status_callback(callback=self.callback)


__all__ = [
    "retro_audio_sample_t",
    "retro_audio_sample_batch_t",
    "retro_audio_sample_batch_float_t",
    "retro_audio_callback_t",
    "retro_audio_set_state_callback_t",
    "retro_audio_buffer_status_callback_t",
    "retro_audio_callback",
    "retro_audio_sample_float_callback",
    "retro_audio_buffer_status_callback",
]
