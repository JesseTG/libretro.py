"""
:class:`~typing.Protocol` definition for MIDI input/output drivers.

.. seealso::

    :mod:`libretro.api.midi`
        The matching :mod:`ctypes` types and callback definitions.
"""

from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class MidiDriver(Protocol):
    """
    Protocol for drivers that expose MIDI input and output streams to a core.

    .. seealso::

        :mod:`libretro.api.midi`
            The matching :mod:`ctypes` types and callback definitions.
    """

    @property
    @abstractmethod
    def input_enabled(self) -> bool:
        """Whether MIDI input is currently enabled."""
        ...

    @property
    @abstractmethod
    def output_enabled(self) -> bool:
        """Whether MIDI output is currently enabled."""
        ...

    @abstractmethod
    def read(self) -> int | None:
        """
        Read the next MIDI byte from the input stream.

        :return: The next byte (0–255), or :obj:`None` if no input is available.

        .. seealso::

            :data:`~libretro.api.midi.retro_midi_read_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def write(self, byte: int, delta_time: int) -> bool:
        """
        Append a single MIDI byte to the output stream.

        :param byte: The MIDI byte (0–255) to write.
        :param delta_time: Time since the previous byte in microseconds.
        :return: :obj:`True` if the byte was buffered for output.

        .. seealso::

            :data:`~libretro.api.midi.retro_midi_write_t`
                The C function pointer type whose signature this method implements.
        """
        ...

    @abstractmethod
    def flush(self) -> bool:
        """
        Send all buffered output bytes to the underlying MIDI device.

        :return: :obj:`True` if the buffer was flushed successfully.

        .. seealso::

            :data:`~libretro.api.midi.retro_midi_flush_t`
                The C function pointer type whose signature this method implements.
        """
        ...


__all__ = ["MidiDriver"]
