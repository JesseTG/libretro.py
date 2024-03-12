from ctypes import CFUNCTYPE, c_bool, Structure, c_uint

from ..._utils import FieldsFromTypeHints

retro_audio_callback_t = CFUNCTYPE(None)
retro_audio_set_state_callback_t = CFUNCTYPE(None, c_bool)


class retro_audio_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_callback_t
    set_state: retro_audio_set_state_callback_t


retro_audio_buffer_status_callback_t = CFUNCTYPE(None, c_bool, c_uint, c_bool)


class retro_audio_buffer_status_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_buffer_status_callback_t
