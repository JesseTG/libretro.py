from ctypes import CFUNCTYPE, POINTER, Structure, c_bool, c_int16, c_size_t, c_uint
from dataclasses import dataclass

from libretro.api._utils import FieldsFromTypeHints

retro_audio_sample_t = CFUNCTYPE(None, c_int16, c_int16)
retro_audio_sample_batch_t = CFUNCTYPE(c_size_t, POINTER(c_int16), c_size_t)
retro_audio_callback_t = CFUNCTYPE(None)
retro_audio_set_state_callback_t = CFUNCTYPE(None, c_bool)
retro_audio_buffer_status_callback_t = CFUNCTYPE(None, c_bool, c_uint, c_bool)


@dataclass(init=False)
class retro_audio_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_callback_t
    set_state: retro_audio_set_state_callback_t

    def __deepcopy__(self, _):
        return retro_audio_callback(callback=self.callback, set_state=self.set_state)


@dataclass(init=False)
class retro_audio_buffer_status_callback(Structure, metaclass=FieldsFromTypeHints):
    callback: retro_audio_buffer_status_callback_t

    def __call__(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        if self.callback:
            self.callback(active, occupancy, underrun_likely)

    def __deepcopy__(self, _):
        return retro_audio_buffer_status_callback(callback=self.callback)


__all__ = [
    "retro_audio_sample_t",
    "retro_audio_sample_batch_t",
    "retro_audio_callback_t",
    "retro_audio_set_state_callback_t",
    "retro_audio_buffer_status_callback_t",
    "retro_audio_callback",
    "retro_audio_buffer_status_callback",
]
