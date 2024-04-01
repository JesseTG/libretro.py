from ctypes import c_int16, POINTER, sizeof
import wave
from io import RawIOBase
from os import PathLike, fsdecode
from pathlib import PurePath

from wave import Wave_write

from .driver import *
from ..defs import *
from ...._utils import memoryview_at


class WaveWriterAudioDriver(AudioDriver):

    def __init__(self, file: str | bytes | PathLike | RawIOBase):
        match file:
            case str() as name:
                self._file = wave.open(name, 'wb')
            case bytes() as name:
                self._file = wave.open(fsdecode(name), 'wb')
            case PathLike() as path:
                self._file = wave.open(fsdecode(path), 'wb')
            case RawIOBase() as io if not io.writable():
                raise ValueError('RawIOBase must be writable')
            case RawIOBase() as io:
                self._file = wave.open(io)
            case _:
                raise TypeError(f'Expected a str, bytes, path, or RawIOBase, got {file!r}')

        self._file.setnchannels(2)
        self._file.setsampwidth(2)
        self._file.setframerate(44100)

    def sample(self, left: int, right: int):
        self._file.writeframesraw(left.to_bytes(2, 'little', signed=True))
        self._file.writeframesraw(right.to_bytes(2, 'little', signed=True))

    def sample_batch(self, data: POINTER(c_int16), frames: int) -> int:
        sample_view = memoryview_at(data, frames * 2 * sizeof(c_int16))
        self._file.writeframesraw(sample_view)

        return frames

    def set_callbacks(self, callback: retro_audio_callback | None) -> bool:
        return False

    def get_callbacks(self) -> retro_audio_callback | None:
        return None

    def get_status_callback(self) -> retro_audio_buffer_status_callback | None:
        return None

    def set_status_callback(self, callback: retro_audio_buffer_status_callback | None) -> bool:
        return False

    def get_minimum_latency(self) -> int | None:
        pass

    def close(self):
        self._file.close()


__all__ = [
    'WaveWriterAudioDriver',
]
