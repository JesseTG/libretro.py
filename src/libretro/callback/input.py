from abc import abstractmethod
from collections.abc import Iterator, Callable
from ctypes import c_int16, c_uint
from typing import Protocol, NamedTuple, runtime_checkable, final, Sequence

from ..defs import InputDeviceFlag


@runtime_checkable
class InputCallbacks(Protocol):
    @abstractmethod
    def poll(self) -> None: ...

    @abstractmethod
    def state(self, port: int, device: InputDeviceFlag, index: int, id: int) -> int: ...


class InputState(InputCallbacks, Protocol):
    @property
    @abstractmethod
    def device_capabilities(self) -> InputDeviceFlag: ...

    @property
    @abstractmethod
    def bitmasks(self) -> bool: ...

    @property
    @abstractmethod
    def max_users(self) -> int: ...

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

    @property
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


InputPollResult = PortState | DeviceState | PointerTouch | int | None
InputStateGenerator = Callable[[], Iterator[InputPollResult | Sequence[InputPollResult]]]


@final
class GeneratorInputState(InputState):
    def __init__(self, generator: InputStateGenerator | None = None):
        self._generator = generator
        self._generator_state: Iterator[InputPollResult | Sequence[InputPollResult]] | None = None
        self._last_poll_result: InputPollResult = None

    def device_capabilities(self) -> InputDeviceFlag:
        pass

    def bitmasks(self) -> bool:
        pass

    def max_users(self) -> int:
        pass

    def poll(self) -> None:
        if self._generator:
            if self._generator_state is None:
                self._generator_state = self._generator()

            self._last_poll_result = next(self._generator_state, None)

    def state(self, port: int, device: InputDeviceFlag, index: int, id: int) -> int:
        match self._last_poll_result:
            case InputPollResult(result):
                return self._convert_to_state(result, port, device, index, id)
            case [*results]:
                return self._convert_to_state(results[port], port, device, index, id)
            case int(value):
                return value
            case None:
                return 0
            case _:
                return 0

    def _convert_to_state(self, result: InputPollResult, port: int, device: InputDeviceFlag, index: int, id: int) -> int:
        match result:
            case JoypadState(joypad) as j:
                return joypad.mask()
            case MouseState(mouse):
                pass
            case KeyboardState(keyboard):
                pass
            case LightGunState(light_gun):
                pass
            case AnalogState(analog):
                pass
            case PointerState(pointer):
                pass
            case PointerTouch(touch):
                pass
            case int(value):
                return value
            case None:
                return 0
            case _:
                return 0
