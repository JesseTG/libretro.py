from ctypes import Structure, c_int16, c_size_t, c_uint
from dataclasses import dataclass
from typing import TYPE_CHECKING

from libretro.typing import (
    ConvertibleToBool,
    ConvertibleToInteger,
    CoreFunctionPointer,
    FrontendFunctionPointer,
    Pointer,
)

retro_audio_sample_t = FrontendFunctionPointer[None, [c_int16, c_int16]]
retro_audio_sample_batch_t = FrontendFunctionPointer[int, [Pointer[c_int16], c_size_t]]
retro_audio_callback_t = CoreFunctionPointer[None, []]
retro_audio_set_state_callback_t = CoreFunctionPointer[None, [ConvertibleToBool]]
retro_audio_buffer_status_callback_t = CoreFunctionPointer[
    None, [ConvertibleToBool, ConvertibleToInteger[c_uint], ConvertibleToBool]
]


@dataclass(init=False)
class retro_audio_callback(Structure):

    if TYPE_CHECKING:
        callback: retro_audio_callback_t | None
        set_state: retro_audio_set_state_callback_t | None

    _fields_ = [
        ("callback", retro_audio_callback_t),
        ("set_state", retro_audio_set_state_callback_t),
    ]

    def __deepcopy__(self, _):
        """
        Returns a copy of this struct with the same callback and set_state.
        Usable with ``copy.deepcopy``.
        """
        return retro_audio_callback(callback=self.callback, set_state=self.set_state)


@dataclass(init=False)
class retro_audio_buffer_status_callback(Structure):
    if TYPE_CHECKING:
        callback: retro_audio_buffer_status_callback_t | None

    _fields_ = [("callback", retro_audio_buffer_status_callback_t)]

    def __call__(self, active: bool, occupancy: int, underrun_likely: bool) -> None:
        """
        Calls ``self.callback`` with the given parameters
        or does nothing if it's ``None``.
        """
        if self.callback:
            self.callback(active, occupancy, underrun_likely)

    def __deepcopy__(self, _):
        """
        Returns a copy of this struct with the same callback.
        Usable with ``copy.deepcopy``.
        """
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
