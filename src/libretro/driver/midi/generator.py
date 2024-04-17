from collections import deque
from collections.abc import Callable, Iterator, Sequence
from typing import NamedTuple

from .driver import MidiDriver

MidiIterator = Iterator[int | None]
MidiGenerator = Callable[[], MidiIterator]


class MidiWrite(NamedTuple):
    byte: int
    delta_time: int


class GeneratorMidiDriver(MidiDriver):
    def __init__(self, generator: MidiGenerator | None = None):
        super().__init__()
        self._generator = generator
        self._generator_state: MidiIterator | None = None
        self._last_poll_result: int | StopIteration | None = None
        self._output: deque[MidiWrite] = deque()
        self._input_enabled = True
        self._output_enabled = True

    @property
    def input_enabled(self) -> bool:
        return (
            self._generator
            and self._input_enabled
            and not isinstance(self._last_poll_result, StopIteration)
        )

    @input_enabled.setter
    def input_enabled(self, value: bool):
        self._input_enabled = bool(value)

    @property
    def output_enabled(self) -> bool:
        return self._output_enabled

    @output_enabled.setter
    def output_enabled(self, value: bool):
        self._output_enabled = bool(value)

    @property
    def output(self) -> Sequence[MidiWrite]:
        return self._output

    def read(self) -> int | None:
        try:
            if self._generator_state is None:
                self._generator_state = self._generator()

            self._last_poll_result = next(self._generator_state, StopIteration())
            match self._last_poll_result:
                case None | int() as i:
                    return i
                case StopIteration() as e:
                    return None
                case _:
                    raise TypeError("MidiGenerator must yield integers or None")
        except StopIteration as e:
            self._last_poll_result = e
            return None

    def write(self, byte: int, delta_time: int) -> bool:
        self._output.append(MidiWrite(byte, delta_time))
        return True

    def flush(self) -> bool:
        self._output.clear()
        return True


__all__ = ["GeneratorMidiDriver"]
