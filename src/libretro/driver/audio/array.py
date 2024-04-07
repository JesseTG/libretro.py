from array import array
from ctypes import sizeof, c_int16, POINTER

from .driver import AudioDriver
from libretro.api.audio import retro_audio_callback, retro_audio_buffer_status_callback
from libretro.api.av import retro_system_av_info
from libretro.api._utils import memoryview_at


class ArrayAudioDriver(AudioDriver):
    def __init__(self):
        self._buffer = array('h')

    def sample(self, left: int, right: int):
        self._buffer.append(left)
        self._buffer.append(right)

    def sample_batch(self, data: POINTER(c_int16), frames: int) -> int:
        sample_view = memoryview_at(data, frames * 2 * sizeof(c_int16))
        self._buffer.frombytes(sample_view)

        return frames

    def set_callbacks(self, callback: retro_audio_callback | None) -> bool:
        return False

    def get_callbacks(self) -> retro_audio_callback | None:
        return None

    def get_status_callback(self) -> retro_audio_buffer_status_callback | None:
        return None  # TODO: Implement

    def set_status_callback(self, callback: retro_audio_buffer_status_callback | None) -> bool:
        return False  # TODO: Implement

    def get_minimum_latency(self) -> int | None:
        return None  # TODO: Implement

    def set_minimum_latency(self, latency: int | None) -> bool:
        return False  # TODO: Implement

    def set_system_av_info(self, info: retro_system_av_info) -> None:
        pass # TODO: Implement
        # TODO: Clear the buffer if the audio frequency is different

    @property
    def buffer(self) -> array:
        return self._buffer


__all__ = [
    'ArrayAudioDriver',
]
