from abc import abstractmethod
from collections.abc import Iterator, Callable
from ctypes import c_int16, c_uint
from typing import Protocol, NamedTuple, runtime_checkable, final, Sequence


@runtime_checkable
class InputCallbacks(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: c_uint, device: c_uint, index: c_uint, id: c_uint) -> c_int16: ...


class DeviceParams(NamedTuple):
    port: int
    device: int
    index: int
    id: int


class JoypadState(NamedTuple):
    b: bool = False
    y: bool = False
    select: bool = False
    start: bool = False
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    a: bool = False
    x: bool = False
    l: bool = False
    r: bool = False
    l2: bool = False
    r2: bool = False
    l3: bool = False
    r3: bool = False

    def mask(self) -> int:
        return (self.b << 0) \
            | (self.y << 1) \
            | (self.select << 2) \
            | (self.start << 3) \
            | (self.up << 4) \
            | (self.down << 5) \
            | (self.left << 6) \
            | (self.right << 7) \
            | (self.a << 8) \
            | (self.x << 9) \
            | (self.l << 10) \
            | (self.r << 11) \
            | (self.l2 << 12) \
            | (self.r2 << 13) \
            | (self.l3 << 14) \
            | (self.r3 << 15)

class MouseState(NamedTuple):
    x: int = 0
    y: int = 0
    left: bool = False
    right: bool = False
    wheel_up: bool = False
    wheel_down: bool = False
    middle: bool = False
    horizontal_wheel_up: bool = False
    horizontal_wheel_down: bool = False
    button4: bool = False
    button5: bool = False

class KeyboardState(NamedTuple):
    pass

class LightGunState(NamedTuple):
    pass

class AnalogState(NamedTuple):
    pass

class PointerTouch(NamedTuple):
    x: int = 0
    y: int = 0

class PointerState(NamedTuple):
    touches: Sequence[PointerTouch] = ()


DeviceState = JoypadState | MouseState | KeyboardState | LightGunState | AnalogState | PointerState

class PortState(NamedTuple):
    joypad: JoypadState | None = None
    mouse: MouseState | None = None
    keyboard: KeyboardState | None = None
    light_gun: LightGunState | None = None
    analog: AnalogState | None = None
    pointer: PointerState | None = None


PortStateGenerator = Callable[[int], Iterator[PortState | DeviceState | int | None]]
PortStateGenerators = Sequence[PortStateGenerator]


@final
class InputState(InputCallbacks):

    def __init__(self, generator: PortStateGenerator | None):
        self._generator = generator
        self._last_state: dict[int, PortState] = {}

    def poll(self) -> None:
        self._last_state.clear()
        if self._generator is not None:
            pass # TODO: Advance each live iterator and store the result in self._last_state

    def state(self, port: c_uint, device: c_uint, index: c_uint, id: c_uint) -> c_int16:
        if port.value not in self._last_state:
            return 0

        pass