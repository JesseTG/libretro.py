from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    c_bool,
    c_int,
    c_int16,
    c_size_t,
    c_uint,
)
from dataclasses import dataclass

from libretro.api._utils import UNCHECKED, FieldsFromTypeHints

RETRO_MICROPHONE_INTERFACE_VERSION = 1
INTERFACE_VERSION = RETRO_MICROPHONE_INTERFACE_VERSION


# This one has no fields, it doesn't need the weight of a metaclass
class retro_microphone(Structure):
    pass


@dataclass(init=False)
class retro_microphone_params(Structure, metaclass=FieldsFromTypeHints):
    rate: c_uint

    def __deepcopy__(self, _):
        return retro_microphone_params(self.rate)


retro_open_mic_t = CFUNCTYPE(
    UNCHECKED(POINTER(retro_microphone)), POINTER(retro_microphone_params)
)
retro_close_mic_t = CFUNCTYPE(None, POINTER(retro_microphone))
retro_get_mic_params_t = CFUNCTYPE(
    c_bool, POINTER(retro_microphone), POINTER(retro_microphone_params)
)
retro_set_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone), c_bool)
retro_get_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone))
retro_read_mic_t = CFUNCTYPE(c_int, POINTER(retro_microphone), POINTER(c_int16), c_size_t)


@dataclass(init=False)
class retro_microphone_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_version: c_uint
    open_mic: retro_open_mic_t
    close_mic: retro_close_mic_t
    get_params: retro_get_mic_params_t
    set_mic_state: retro_set_mic_state_t
    get_mic_state: retro_get_mic_state_t
    read_mic: retro_read_mic_t

    def __deepcopy__(self, _):
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
