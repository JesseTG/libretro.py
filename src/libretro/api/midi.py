"""
MIDI input/output interface types.
Allows cores to send and receive MIDI messages.

Corresponds to :c:type:`retro_midi_interface` in ``libretro.h``.

.. seealso::
    :class:`.MidiDriver`
        The :class:`.Protocol` that uses these types to implement MIDI support in libretro.py.

    :mod:`libretro.drivers.midi`
        libretro.py's included :class:`.MidiDriver` implementations.
"""

from ctypes import Structure, c_bool, c_uint8, c_uint32
from dataclasses import dataclass

from libretro.ctypes import CIntArg, TypedFunctionPointer, TypedPointer

retro_midi_input_enabled_t = TypedFunctionPointer[c_bool, []]
"""Returns whether MIDI input is enabled."""

retro_midi_output_enabled_t = TypedFunctionPointer[c_bool, []]
"""Returns whether MIDI output is enabled."""

retro_midi_read_t = TypedFunctionPointer[c_bool, [TypedPointer[c_uint8]]]
"""Reads a byte from the MIDI input stream."""

retro_midi_write_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint8], CIntArg[c_uint32]]]
"""Writes a byte to the MIDI output stream with a delta time."""

retro_midi_flush_t = TypedFunctionPointer[c_bool, []]
"""Flushes the MIDI output stream."""


@dataclass(init=False, slots=True)
class retro_midi_interface(Structure):
    """
    Provides functions for MIDI input/output.

    Corresponds to :c:type:`retro_midi_interface` in ``libretro.h``.

    >>> from libretro.api import retro_midi_interface
    >>> midi = retro_midi_interface()
    >>> midi.read is None
    True
    """

    input_enabled: retro_midi_input_enabled_t | None
    """Returns whether MIDI input is enabled."""
    output_enabled: retro_midi_output_enabled_t | None
    """Returns whether MIDI output is enabled."""
    read: retro_midi_read_t | None
    """Reads a byte from the MIDI input stream."""
    write: retro_midi_write_t | None
    """Writes a byte to the MIDI output stream with a delta time."""
    flush: retro_midi_flush_t | None
    """Flushes previously-written MIDI data."""

    _fields_ = (
        ("input_enabled", retro_midi_input_enabled_t),
        ("output_enabled", retro_midi_output_enabled_t),
        ("read", retro_midi_read_t),
        ("write", retro_midi_write_t),
        ("flush", retro_midi_flush_t),
    )

    def __deepcopy__(self, _):
        """
        Returns a copy of this object.
        Intended for use with :func:`copy.deepcopy`.

        >>> import copy
        >>> from libretro.api import retro_midi_interface
        >>> copy.deepcopy(retro_midi_interface()).read is None
        True
        """
        return retro_midi_interface(
            self.input_enabled, self.output_enabled, self.read, self.write, self.flush
        )


__all__ = [
    "retro_midi_input_enabled_t",
    "retro_midi_output_enabled_t",
    "retro_midi_read_t",
    "retro_midi_write_t",
    "retro_midi_flush_t",
    "retro_midi_interface",
]
