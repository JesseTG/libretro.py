"""
:class:`.MidiDriver` implementation that streams events produced by a generator function.

.. seealso::

    :class:`.MidiDriver`
        The protocol this driver implements.
"""

from collections import deque
from collections.abc import Callable, Iterator, Sequence
from typing import NamedTuple, override

from .driver import MidiDriver

MidiIterator = Iterator[int | None]
MidiGenerator = Callable[[], MidiIterator]


class MidiWrite(NamedTuple):
    byte: int
    delta_time: int


class GeneratorMidiDriver(MidiDriver):
    """
    A :class:`.MidiDriver` that streams input bytes from a generator function.

    Output bytes are appended to an in-memory buffer
    accessible through :attr:`output` so tests can assert on what the core sent.

    .. seealso::

        :class:`.MidiDriver`
            The protocol this class implements.
    """

    def __init__(self, generator: MidiGenerator | None = None):
        """
        Initialize the driver with an optional MIDI input source.

        :param generator: A callable returning an iterator of MIDI input bytes
            (or :obj:`None` for "no byte this poll"),
            or :obj:`None` to disable MIDI input entirely.
        """
        super().__init__()
        self._generator = generator
        self._generator_state: MidiIterator | None = None
        self._last_poll_result: int | StopIteration | None = None
        self._output: deque[MidiWrite] = deque()
        self._input_enabled = True
        self._output_enabled = True

    @property
    @override
    def input_enabled(self) -> bool:
        return bool(
            self._generator
            and self._input_enabled
            and not isinstance(self._last_poll_result, StopIteration)
        )

    @input_enabled.setter
    def input_enabled(self, value: bool):
        self._input_enabled = bool(value)

    @property
    @override
    def output_enabled(self) -> bool:
        return self._output_enabled

    @output_enabled.setter
    def output_enabled(self, value: bool):
        self._output_enabled = bool(value)

    @property
    def output(self) -> Sequence[MidiWrite]:
        """The buffered :class:`MidiWrite` events produced by the core, in send order."""
        return self._output

    @override
    def read(self) -> int | None:
        if not self._generator:
            return None

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

    @override
    def write(self, byte: int, delta_time: int) -> bool:
        self._output.append(MidiWrite(byte, delta_time))
        return True

    @override
    def flush(self) -> bool:
        self._output.clear()
        return True


__all__ = ["GeneratorMidiDriver"]
