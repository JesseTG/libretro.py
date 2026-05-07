"""
:class:`~typing.Protocol` definitions for microphone capture drivers.

.. seealso::

    :mod:`libretro.api.microphone`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from array import array
from collections.abc import Collection
from typing import Protocol, runtime_checkable

from libretro.api.microphone import retro_microphone, retro_microphone_params


@runtime_checkable
class Microphone(Protocol):
    """Protocol for an open microphone capture stream returned by a :class:`MicrophoneDriver`."""

    @abstractmethod
    def close(self) -> None:
        """
        Close this microphone and release any underlying resources.

        Subsequent calls to :meth:`read` should return :obj:`None`.
        """
        ...

    @property
    @abstractmethod
    def params(self) -> retro_microphone_params | None:
        """
        The capture parameters (sample rate, channel layout) negotiated for this microphone.

        :obj:`None` if the microphone is closed or no parameters have been negotiated.

        .. seealso::

            :class:`~libretro.api.microphone.retro_microphone_params`
                The C struct describing the negotiated capture format.
        """
        ...

    @abstractmethod
    def read(self, frames: int) -> array[int] | None:
        """
        Read up to ``frames`` audio frames from this microphone.

        :param frames: Maximum number of mono signed 16-bit frames to read.
        :return: An :class:`array.array` of signed 16-bit samples
            holding the frames actually read, or :obj:`None` if the microphone
            is closed or no samples are available.
        """
        ...

    @property
    @abstractmethod
    def state(self) -> bool:
        """
        Whether this microphone is currently capturing.

        :param state: :obj:`True` to start capturing, :obj:`False` to pause it.
        """
        ...

    @state.setter
    @abstractmethod
    def state(self, state: bool) -> None:
        """See :attr:`state`."""
        ...

    def poll(self) -> None:
        """
        Advance any per-frame internal state (e.g. refilling the capture buffer).

        Default implementation is a no-op;
        drivers that need per-frame work override this.
        """
        pass


@runtime_checkable
class MicrophoneDriver(Protocol):
    """
    Protocol for drivers that expose the libretro microphone capture interface.

    .. seealso::

        :mod:`libretro.api.microphone`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def version(self) -> int:
        """The version of the microphone interface this driver implements."""
        ...

    @abstractmethod
    def open_mic(self, params: retro_microphone_params | None) -> retro_microphone | None:
        """
        Open a new microphone capture stream.

        :param params: Requested capture parameters,
            or :obj:`None` to let the driver pick its defaults.
        :return: A handle to the opened microphone,
            or :obj:`None` if no microphone could be opened.
        """
        ...

    @abstractmethod
    def close_mic(self, mic: retro_microphone) -> None:
        """
        Close a microphone previously returned by :meth:`open_mic`.

        :param mic: The microphone handle to close.
        """
        ...

    @abstractmethod
    def get_mic_params(self, mic: retro_microphone) -> retro_microphone_params | None:
        """
        Return the negotiated capture parameters for ``mic``.

        :param mic: The microphone handle to query.
        :return: The negotiated parameters,
            or :obj:`None` if the microphone has none.
        """
        ...

    @abstractmethod
    def get_mic_state(self, mic: retro_microphone) -> bool:
        """
        Return whether ``mic`` is currently capturing.

        :param mic: The microphone handle to query.
        :return: :obj:`True` if the microphone is capturing.
        """
        ...

    @abstractmethod
    def set_mic_state(self, mic: retro_microphone, state: bool) -> None:
        """
        Start or pause capture on ``mic``.

        :param mic: The microphone handle to update.
        :param state: :obj:`True` to start capturing, :obj:`False` to pause.
        """
        ...

    @abstractmethod
    def read_mic(self, mic: retro_microphone, frames: int) -> array[int] | None:
        """
        Read up to ``frames`` audio frames from ``mic``.

        :param mic: The microphone handle to read from.
        :param frames: Maximum number of mono signed 16-bit frames to read.
        :return: An :class:`array.array` of signed 16-bit samples
            holding the frames actually read, or :obj:`None` if the microphone
            is closed or no samples are available.
        """
        ...

    @property
    @abstractmethod
    def microphones(self) -> Collection[Microphone]:
        """All microphones currently open through this driver."""
        ...


__all__ = ["Microphone", "MicrophoneDriver"]
