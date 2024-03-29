from array import array
from collections.abc import Sequence, Iterator, Callable

from .defs import retro_microphone_params
from .interface import *

from ...h import RETRO_MICROPHONE_INTERFACE_VERSION

MicrophoneInput = int | Sequence[int] | None
MicrophoneInputIterator = Iterator[MicrophoneInput]
MicrophoneInputGenerator = Callable[[], MicrophoneInputIterator]


class GeneratorMicrophone(Microphone):
    def __init__(self, generator: MicrophoneInputGenerator | None, params: retro_microphone_params | None):
        super().__init__(params)
        self._params = params or retro_microphone_params(44100)
        self._enabled = False
        self._generator = generator
        self._generator_state: MicrophoneInputIterator | None = None
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def get_params(self) -> retro_microphone_params | None:
        if self._closed:
            return None

        return self._params

    def set_state(self, state: bool) -> bool:
        if self._closed:
            return False

        self._enabled = bool(state)
        return True

    def get_state(self) -> bool:
        if self._closed:
            return False

        return self._enabled

    def read(self, frames: int) -> Sequence[int]:
        if self._closed or not self._enabled or not frames:
            # If this mic is closed, off, or asked to provide zero samples...
            return ()

        if not self._generator_state:
            self._generator_state = self._generator()

        buffer = array('h')
        try:
            while len(buffer) < frames:
                match next(self._generator_state, None):
                    case None:
                        break
                    case int(frame):
                        buffer.append(frame)
                    case array() as samples if samples.typecode == 'h':
                        buffer.extend(samples)
                    case f if isinstance(f, Sequence):
                        buffer.extend(f)
                    case f:
                        raise TypeError(f"MicrophoneInputGenerator must yield a signed 16-bit integer, an array of them, or None; got {type(f).__name__}")

        except StopIteration:
            # Not actually an error, just means the generator is done
            return buffer
        except Exception as e:
            # TODO: Log error
            return ()

        return buffer


class GeneratorMicrophoneInterface(MicrophoneInterface):
    def __init__(self, generator: MicrophoneInputGenerator | None = None):
        super().__init__()
        self._generator = generator

    @property
    def version(self) -> int:
        return RETRO_MICROPHONE_INTERFACE_VERSION

    def open_mic(self, params: retro_microphone_params | None) -> Microphone:
        return GeneratorMicrophone(self._generator, params)


__all__ = [
    'GeneratorMicrophone',
    'GeneratorMicrophoneInterface',
    'MicrophoneInput',
    'MicrophoneInputIterator',
    'MicrophoneInputGenerator'
]