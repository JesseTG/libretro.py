from ctypes import CFUNCTYPE, POINTER, Structure, c_bool, c_uint8, c_uint32
from dataclasses import dataclass

from libretro.api._utils import FieldsFromTypeHints

retro_midi_input_enabled_t = CFUNCTYPE(c_bool)
retro_midi_output_enabled_t = CFUNCTYPE(c_bool)
retro_midi_read_t = CFUNCTYPE(c_bool, POINTER(c_uint8))
retro_midi_write_t = CFUNCTYPE(c_bool, c_uint8, c_uint32)
retro_midi_flush_t = CFUNCTYPE(c_bool)


@dataclass(init=False)
class retro_midi_interface(Structure, metaclass=FieldsFromTypeHints):
    input_enabled: retro_midi_input_enabled_t
    output_enabled: retro_midi_output_enabled_t
    read: retro_midi_read_t
    write: retro_midi_write_t
    flush: retro_midi_flush_t

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
