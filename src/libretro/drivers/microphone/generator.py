from array import array
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from itertools import repeat
from typing import override

from libretro.api.microphone import (
    INTERFACE_VERSION,
    retro_microphone,
    retro_microphone_params,
)

from .driver import Microphone, MicrophoneDriver

MicrophoneInput = int | Sequence[int] | None
MicrophoneInputIterator = Iterator[MicrophoneInput]
MicrophoneInputIterable = Iterable[MicrophoneInput]
MicrophoneInputGenerator = Callable[[], MicrophoneInputIterator]
MicrophoneSource = MicrophoneInputIterable | MicrophoneInputGenerator


class GeneratorMicrophone(Microphone):
    _generator_state: MicrophoneInputIterator

    def __init__(self, generator: MicrophoneSource | None, params: retro_microphone_params | None):
        self._params = params or retro_microphone_params(44100)
        self._enabled = False
        self._closed = False
        self._overflow = array("h")

        match generator:
            case None:
                self._generator_state = repeat(0)
            case Callable():
                self._generator_state = generator()
            case Iterable() as it:
                self._generator_state = iter(it)

    @override
    def close(self) -> None:
        self._closed = True

    @property
    @override
    def params(self) -> retro_microphone_params | None:
        if self._closed:
            return None

        return self._params

    @property
    @override
    def state(self) -> bool:
        if self._closed:
            return False

        return self._enabled

    @state.setter
    @override
    def state(self, state: bool) -> None:
        if self._closed:
            raise RuntimeError("Cannot set state on a closed microphone")

        self._enabled = bool(state)

    @override
    def read(self, frames: int) -> array[int] | None:
        if self._closed or not self._enabled or not frames:
            # If this mic is closed, off, or asked to provide zero samples...
            return None

        buffer = array("h", self._overflow)
        self._overflow.clear()

        while len(buffer) < frames:
            # Until we have the requested number of frames in the buffer,
            # keep asking the generator for more input and filling the buffer with it.
            match next(self._generator_state, None):
                case None:
                    buffer.append(0)
                case int(frame):
                    buffer.append(frame)
                case array() as samples if samples.typecode == "h":
                    buffer.extend(samples)
                case f if isinstance(f, Sequence):
                    buffer.extend(f)
                case f:
                    raise TypeError(
                        f"MicrophoneInputGenerator must yield a signed 16-bit integer, an array of them, or None; got {type(f).__name__}"
                    )

        if len(buffer) > frames:
            # If we got more frames than requested, save the excess in the overflow buffer for next time.
            self._overflow.extend(buffer[frames:])
            del buffer[frames:]
            assert len(buffer) <= frames

        return buffer


class GeneratorMicrophoneDriver(MicrophoneDriver):
    def __init__(
        self, generator: MicrophoneInputGenerator | MicrophoneInputIterable | None = None
    ):
        self._microphones: dict[int, GeneratorMicrophone] = {}
        self._generator = generator

    @property
    @override
    def version(self) -> int:
        return INTERFACE_VERSION

    @override
    def open_mic(self, params: retro_microphone_params | None) -> retro_microphone | None:
        mic = GeneratorMicrophone(self._generator, params)
        mic_id = id(mic)
        handle = retro_microphone(mic_id)
        self._microphones[mic_id] = mic
        return handle

    @override
    def close_mic(self, mic: retro_microphone) -> None:
        mic_id = mic.id
        if m := self._microphones.get(mic_id):
            m.close()
            del self._microphones[mic_id]

    @override
    def get_mic_params(self, mic: retro_microphone) -> retro_microphone_params | None:
        mic_id = mic.id
        if (m := self._microphones.get(mic_id)) is not None:
            return m.params

        return None

    @override
    def get_mic_state(self, mic: retro_microphone) -> bool:
        mic_id = mic.id
        if (m := self._microphones.get(mic_id)) is not None:
            return m.state

        return False

    @override
    def set_mic_state(self, mic: retro_microphone, state: bool) -> None:
        mic_id = mic.id
        if (m := self._microphones.get(mic_id)) is not None:
            m.state = state

    @override
    def read_mic(self, mic: retro_microphone, frames: int) -> array[int] | None:
        mic_id = mic.id
        if (m := self._microphones.get(mic_id)) is not None:
            return m.read(frames)

        return None

    @property
    @override
    def microphones(self) -> Collection[GeneratorMicrophone]:
        return self._microphones.values()


__all__ = [
    "GeneratorMicrophone",
    "GeneratorMicrophoneDriver",
    "MicrophoneInput",
    "MicrophoneInputIterator",
    "MicrophoneInputGenerator",
    "MicrophoneSource",
]
