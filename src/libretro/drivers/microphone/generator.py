from array import array
from collections.abc import Callable, Generator, Iterable, Iterator, Sequence

from libretro._typing import override
from libretro.api.microphone import INTERFACE_VERSION, retro_microphone_params

from .driver import Microphone, MicrophoneDriver

MicrophoneInput = int | Sequence[int] | None
MicrophoneInputIterator = Iterator[MicrophoneInput]
MicrophoneInputGenerator = Callable[[], MicrophoneInputIterator]
MicrophoneSource = MicrophoneInput | MicrophoneInputIterator | MicrophoneInputGenerator


class GeneratorMicrophone(Microphone):
    def __init__(self, generator: MicrophoneSource | None, params: retro_microphone_params | None):
        super().__init__(params)
        self._params = params or retro_microphone_params(44100)
        self._enabled = False
        self._generator = generator
        self._generator_state: MicrophoneInputIterator | None = None
        self._closed = False

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

    def read(self, frames: int) -> Sequence[int]:
        if self._closed or not self._enabled or not frames:
            # If this mic is closed, off, or asked to provide zero samples...
            return ()

        if self._generator_state is None and self._generator:
            match self._generator:
                case Callable() as func:
                    self._generator_state = func()
                case Iterable() | Iterator() | Generator() as it:
                    self._generator_state = it

        buffer = array("h")
        try:
            while len(buffer) < frames:
                match next(self._generator_state, None):
                    case None:
                        break
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

        except StopIteration:
            # Not actually an error, just means the generator is done
            return buffer
        except Exception as e:
            # TODO: Log error
            return ()

        return buffer


class GeneratorMicrophoneDriver(MicrophoneDriver):
    def __init__(self, generator: MicrophoneInputGenerator | None = None):
        super().__init__()
        self._generator = generator

    @property
    def version(self) -> int:
        return INTERFACE_VERSION

    def open_mic(self, params: retro_microphone_params | None) -> Microphone:
        return GeneratorMicrophone(self._generator, params)


__all__ = [
    "GeneratorMicrophone",
    "GeneratorMicrophoneDriver",
    "MicrophoneInput",
    "MicrophoneInputIterator",
    "MicrophoneInputGenerator",
    "MicrophoneSource",
]
