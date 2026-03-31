from ctypes import Structure, c_bool, c_uint8, c_uint32
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libretro.typing import CIntArg, TypedFunctionPointer, TypedPointer

retro_midi_input_enabled_t = TypedFunctionPointer[c_bool, []]
retro_midi_output_enabled_t = TypedFunctionPointer[c_bool, []]
retro_midi_read_t = TypedFunctionPointer[c_bool, [TypedPointer[c_uint8]]]
retro_midi_write_t = TypedFunctionPointer[c_bool, [CIntArg[c_uint8], CIntArg[c_uint32]]]
retro_midi_flush_t = TypedFunctionPointer[c_bool, []]


@dataclass(init=False)
class retro_midi_interface(Structure):
    if TYPE_CHECKING:
        input_enabled: retro_midi_input_enabled_t | None
        output_enabled: retro_midi_output_enabled_t | None
        read: retro_midi_read_t | None
        write: retro_midi_write_t | None
        flush: retro_midi_flush_t | None

    _fields_ = [
        ("input_enabled", retro_midi_input_enabled_t),
        ("output_enabled", retro_midi_output_enabled_t),
        ("read", retro_midi_read_t),
        ("write", retro_midi_write_t),
        ("flush", retro_midi_flush_t),
    ]

    def __deepcopy__(self, _):
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
