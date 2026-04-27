"""
Defines an interface for audio output functionality in libretro.py.

.. seealso::
    :mod:`libretro.api.audio`
        Provides the C callback and struct types that :class:`.AudioDriver` implementations use.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable

from libretro.api import (
    retro_audio_buffer_status_callback,
    retro_audio_callback,
    retro_system_av_info,
)


@runtime_checkable
class AudioDriver(Protocol):
    """
    Protocol for drivers that receive audio output from the core.

    Can be used with :func:`isinstance`.

    .. seealso::

        :mod:`libretro.api.audio`
            The C callback types and sample function signatures
            that implementations of this protocol accept.
    """

    @abstractmethod
    def sample(self, left: int, right: int) -> None:
        """
        Receives a single stereo audio sample from the core.

        :param left: The left-channel sample as a signed 16-bit integer.
        :param right: The right-channel sample as a signed 16-bit integer.

        .. seealso::

            :class:`~libretro.api.audio.retro_audio_sample_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def sample_batch(self, frames: memoryview) -> int:
        """
        Receives a batch of interleaved stereo audio frames from the core.

        :param frames: A read-only :class:`memoryview` of interleaved signed 16-bit stereo frames.
        :return: The number of frames consumed.

        .. seealso::

            :class:`~libretro.api.audio.retro_audio_sample_batch_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @property
    @abstractmethod
    def callbacks(self) -> retro_audio_callback | None:
        """
        The asynchronous audio callback registered by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_AUDIO_CALLBACK``.

        .. seealso::

            :class:`~libretro.api.audio.retro_audio_callback`
                The C struct registered by the core that contains this callback.
        """
        ...

    @callbacks.setter
    @abstractmethod
    def callbacks(self, callback: retro_audio_callback | None) -> None:
        """
        :param callback: The audio callback to register, or :obj:`None` to clear it.
        :raises UnsupportedEnvCall: If this driver does not support asynchronous audio callbacks.
        """
        ...

    def set_state(self, enabled: bool) -> None:
        """
        Enables or disables the registered asynchronous audio callback.

        Calls :attr:`retro_audio_callback.set_state` if a callback is registered.

        :param enabled: Whether to enable the audio callback.
        """
        callbacks = self.callbacks
        if callbacks and callbacks.set_state:
            callbacks.set_state(enabled)

    def callback(self) -> None:
        """
        Invokes the registered asynchronous audio callback, if any.

        Calls :attr:`retro_audio_callback.callback` if a callback is registered.
        """
        callbacks = self.callbacks
        if callbacks and callbacks.callback:
            callbacks.callback()

    @property
    @abstractmethod
    def buffer_status(self) -> retro_audio_buffer_status_callback | None:
        """
        The buffer-status callback registered by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK``.

        .. seealso::

            :class:`~libretro.api.audio.retro_audio_buffer_status_callback`
                The C struct registered by the core that contains this callback.
        """
        ...

    @buffer_status.setter
    @abstractmethod
    def buffer_status(self, callback: retro_audio_buffer_status_callback | None) -> None:
        """
        :param callback: The buffer-status callback to register, or :obj:`None` to clear it.
        :raises UnsupportedEnvCall: If this driver does not support the buffer-status callback.
        """
        ...

    def report_buffer_status(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        """
        Invokes the registered buffer-status callback, if any.

        :param active: Whether the audio buffer is actively being filled.
        :param occupancy: The percentage of the buffer that is currently filled (0–100).
        :param underrun_likely: Whether a buffer underrun is likely on the next frame.
        """
        callback = self.buffer_status
        if callback:
            callback(active, occupancy, underrun_likely)

    @property
    @abstractmethod
    def minimum_latency(self) -> int | None:
        """
        The minimum audio latency in milliseconds requested by the core, if any.

        Set via ``RETRO_ENVIRONMENT_SET_MINIMUM_AUDIO_LATENCY``.
        :obj:`None` if the core has not set a minimum latency.
        """
        ...

    @minimum_latency.setter
    @abstractmethod
    def minimum_latency(self, latency: int | None) -> None:
        """
        :param latency: The minimum audio latency in milliseconds, or :obj:`None` to clear it.
        :raises UnsupportedEnvCall: If this driver does not support minimum latency configuration.
        """
        ...

    @property
    @abstractmethod
    def system_av_info(self) -> retro_system_av_info | None:
        """
        The AV info most recently set by the core.

        Used by the driver to configure audio parameters such as sample rate.
        """
        ...

    @system_av_info.setter
    @abstractmethod
    def system_av_info(self, info: retro_system_av_info) -> None:
        """
        :param info: The :class:`~libretro.api.av.retro_system_av_info` reported by the core.
        :raises TypeError: If ``info`` is not a :class:`~libretro.api.av.retro_system_av_info`.
        """
        ...


__all__ = [
    "AudioDriver",
]
