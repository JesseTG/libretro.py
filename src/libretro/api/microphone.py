from ctypes import *

from .._utils import FieldsFromTypeHints, UNCHECKED


# This one has no fields, it doesn't need the weight of a metaclass
class retro_microphone(Structure):
    pass


class retro_microphone_params(Structure, metaclass=FieldsFromTypeHints):
    rate: c_uint


retro_open_mic_t = CFUNCTYPE(UNCHECKED(POINTER(retro_microphone)), POINTER(retro_microphone_params))
retro_close_mic_t = CFUNCTYPE(None, POINTER(retro_microphone))
retro_get_mic_params_t = CFUNCTYPE(c_bool, POINTER(retro_microphone), POINTER(retro_microphone_params))
retro_set_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone), c_bool)
retro_get_mic_state_t = CFUNCTYPE(c_bool, POINTER(retro_microphone))
retro_read_mic_t = CFUNCTYPE(c_int, POINTER(retro_microphone), POINTER(c_int16), c_size_t)


class retro_microphone_interface(Structure, metaclass=FieldsFromTypeHints):
    interface_version: c_uint
    open_mic: retro_open_mic_t
    close_mic: retro_close_mic_t
    get_params: retro_get_mic_params_t
    set_mic_state: retro_set_mic_state_t
    get_mic_state: retro_get_mic_state_t
    read_mic: retro_read_mic_t
