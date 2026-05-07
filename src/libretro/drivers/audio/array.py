"""
An audio driver that accumulates all received samples in an :class:`~array.array`.

.. seealso::

    :mod:`libretro.api.audio`
        Defines the audio callback types and sample formats this driver handles.
"""

from array import array
from copy import deepcopy
from typing import override

from libretro.api.audio import retro_audio_buffer_status_callback, retro_audio_callback
from libretro.api.av import retro_system_av_info
from libretro.error import UnsupportedEnvCall

from .driver import AudioDriver


class ArrayAudioDriver(AudioDriver):
    """
    A basic :class:`.AudioDriver` that stores all audio samples in an in-memory :class:`~array.array`.

    Suitable for tests that need to inspect audio output after the fact.
    """

    def __init__(self):
        """Initialize with an empty :class:`~array.array` and no AV info."""
        self._buffer = array("h")
        self._system_av_info: retro_system_av_info | None = None

    @override
    def sample(self, left: int, right: int):
        self._buffer.append(left)
        self._buffer.append(right)

    @override
    def sample_batch(self, frames: memoryview) -> int:
        if frames.format != "h":
            byte_view = frames.cast("B")
            sample_view = byte_view.cast("h")
        else:
            sample_view = frames

        self._buffer.extend(sample_view)

        # Divide by two to return number of frames
        return len(sample_view) // 2

    @property
    @override
    def callbacks(self) -> retro_audio_callback | None:
        """
        Audio callbacks are not supported by this driver.

        :return: :obj:`None`, always.
        :raises UnsupportedEnvCall: If setting this property.
        """
        return None

    @callbacks.setter
    @override
    def callbacks(self, callback: retro_audio_callback | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting callbacks")

    @property
    @override
    def buffer_status(self) -> retro_audio_buffer_status_callback | None:
        """
        Buffer-status callbacks are not supported by this driver.

        :return: :obj:`None`, always.
        :raises UnsupportedEnvCall: If setting this property.
        """
        return None

    @buffer_status.setter
    @override
    def buffer_status(self, callback: retro_audio_buffer_status_callback | None):
        raise UnsupportedEnvCall(
            "ArrayAudioDriver does not support setting buffer status callback"
        )

    @property
    @override
    def minimum_latency(self) -> int | None:
        """
        Setting a minimum latency is not supported by this driver.

        :return: :obj:`None`, always.
        :raises UnsupportedEnvCall: If setting this property.
        """
        return None

    @minimum_latency.setter
    @override
    def minimum_latency(self, latency: int | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting minimum latency")

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info)

    @system_av_info.setter
    @override
    def system_av_info(self, info: retro_system_av_info):
        if not isinstance(info, retro_system_av_info):
            raise TypeError(f"Expected retro_system_av_info; got {type(info).__name__}")

        self._system_av_info = deepcopy(info)

    @property
    def buffer(self) -> array[int]:
        """The accumulated audio data as an :class:`~array.array` of signed 16-bit interleaved stereo samples."""
        return self._buffer


__all__ = [
    "ArrayAudioDriver",
]
