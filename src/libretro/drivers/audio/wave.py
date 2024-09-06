import wave
from copy import deepcopy
from io import RawIOBase
from os import PathLike, fsdecode

from libretro._typing import override
from libretro.api.audio import retro_audio_buffer_status_callback, retro_audio_callback
from libretro.api.av import retro_system_av_info
from libretro.error import UnsupportedEnvCall

from .driver import AudioDriver


class WaveWriterAudioDriver(AudioDriver):
    def __init__(self, file: str | bytes | PathLike | RawIOBase):
        match file:
            case str() as name:
                self._file = wave.open(name, "wb")
            case bytes() as name:
                self._file = wave.open(fsdecode(name), "wb")
            case PathLike() as path:
                self._file = wave.open(fsdecode(path), "wb")
            case RawIOBase() as io if not io.writable():
                raise ValueError("RawIOBase must be writable")
            case RawIOBase() as io:
                self._file = wave.open(io)
            case _:
                raise TypeError(f"Expected a str, bytes, path, or RawIOBase, got {file!r}")

        self._file.setnchannels(2)
        self._file.setsampwidth(2)
        self._file.setframerate(44100)
        self._system_av_info: retro_system_av_info | None = None

    def sample(self, left: int, right: int):
        self._file.writeframesraw(left.to_bytes(2, "little", signed=True))
        self._file.writeframesraw(right.to_bytes(2, "little", signed=True))

    def sample_batch(self, data: memoryview) -> int:
        self._file.writeframesraw(data)

        # Divide by two to return number of frames
        return len(memoryview) // 2

    @property
    @override
    def callbacks(self) -> retro_audio_callback | None:
        return None

    @callbacks.setter
    @override
    def callbacks(self, callback: retro_audio_callback | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting callbacks")

    @property
    @override
    def buffer_status(self) -> retro_audio_buffer_status_callback | None:
        return None

    @buffer_status.setter
    @override
    def buffer_status(self, callback: retro_audio_buffer_status_callback):
        raise UnsupportedEnvCall(
            "ArrayAudioDriver does not support setting buffer status callback"
        )

    @property
    @override
    def minimum_latency(self) -> int | None:
        return None

    @minimum_latency.setter
    @override
    def minimum_latency(self, latency: int | None):
        raise UnsupportedEnvCall("ArrayAudioDriver does not support setting minimum latency")

    @property
    @override
    def system_av_info(self) -> retro_system_av_info | None:
        return deepcopy(self._system_av_info)

    @system_av_info.setter
    @override
    def system_av_info(self, info: retro_system_av_info):
        if not isinstance(info, retro_system_av_info):
            raise TypeError(f"Expected retro_system_av_info; got {type(info).__name__}")

        self._system_av_info = deepcopy(info)

    def close(self):
        self._file.close()


__all__ = [
    "WaveWriterAudioDriver",
]
